from playwright.sync_api import sync_playwright
# from solver import solve_question
from solver import solve_questions
import re
from config import EMAIL, NAME, ROLL_NO, BRANCH, AUTO_SUBMIT

# FORM_URL = "https://forms.gle/8zktThq7p1STTWAr5"

def select_answer(group, answer, option_text):

    radios = group.locator('[role="radio"]')

    target_text = option_text.strip().lower()

    for i in range(radios.count()):

        radio = radios.nth(i)

        data_value = (radio.get_attribute("data-value") or "").strip()
        aria_label = (radio.get_attribute("aria-label") or "").strip()

        if not data_value and not aria_label:
            continue

        data_value_clean = data_value.lower()
        aria_label_clean = aria_label.lower()

        if (
            target_text == data_value_clean
            or target_text in data_value_clean
            or target_text in aria_label_clean
        ):

            label = radio.locator("xpath=ancestor::label[1]")
            label.click()

            # Verify selection
            group.page.wait_for_timeout(100)

            if radio.get_attribute("aria-checked") == "true":
                print(f"  ✓ Selected {answer}: {option_text}")
                return

            # Sometimes Google Forms updates after a tiny delay
            group.page.wait_for_timeout(300)

            if radio.get_attribute("aria-checked") == "true":
                print(f"  ✓ Selected {answer}: {option_text}")
                return

            raise RuntimeError(
                f"Clicked {answer}, but Google Forms did not check it."
            )

    raise RuntimeError(
        f"Could not find option {answer}: {option_text}"
    )

def get_valid_options(group):
    radios = group.locator('[role="radio"]')
    valid = []

    for i in range(radios.count()):
        radio = radios.nth(i)

        data_value = (radio.get_attribute("data-value") or "").strip()
        aria_label = (radio.get_attribute("aria-label") or "").strip()

        value = data_value or aria_label

        if value:
            valid.append(radio)

    return valid

# def select_answer(group, answer, option_text):

#     radios = group.locator('[role="radio"]')

#     for i in range(radios.count()):

#         radio = radios.nth(i)

#         aria_label = radio.get_attribute("aria-label") or ""
#         data_value = radio.get_attribute("data-value") or ""

#         # Ignore empty/invalid radio elements
#         if not aria_label and not data_value:
#             continue

#         # Match the actual option text
#         if option_text.strip().lower() in aria_label.strip().lower():
#             radio.click()
#             return

#         if option_text.strip().lower() == data_value.strip().lower():
#             radio.click()
#             return

#     raise RuntimeError(
#         f"Could not find option {answer}: {option_text}"
#     )


def check_record_email(page):
    checkbox = page.locator(
        '[role="checkbox"][aria-label*="Record"][aria-label*="email"]'
    )

    if checkbox.count() == 0:
        print("Record email checkbox not found")
        return

    checkbox = checkbox.first

    if checkbox.get_attribute("aria-checked") != "true":
        checkbox.click()
        print("Record email: checked")
    else:
        print("Record email: already checked")

def parse_question(text):
    text = text.replace("Untitled Question", "")
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    # Remove Google Forms metadata
    lines = [
        line for line in lines
        if line not in ["*", "0 points", "1 point"]
    ]

    question = ""
    options = {}

    # Check whether options have A/B/C/D labels
    labeled_options = []

    for line in lines:
        match = re.match(r"^([A-Da-d])[\.\)]\s*(.*)", line)

        if match:
            labeled_options.append(
                (
                    match.group(1).upper(),
                    match.group(2).strip()
                )
            )

    if len(labeled_options) == 4:

        # Existing format:
        # A. ...
        # B. ...
        # C. ...
        # D. ...

        for letter, option in labeled_options:
            options[letter] = option

        for line in lines:
            if not re.match(r"^([A-Da-d])[\.\)]\s*", line):
                question = re.sub(
                    r"^\d+\.\s*",
                    "",
                    line
                )
                break

    else:

        # Unlabelled format:
        # question
        # option
        # option
        # option
        # option

        question = re.sub(
            r"^\d+\.\s*",
            "",
            lines[0]
        )

        option_lines = lines[1:]

        if len(option_lines) < 4:
            raise ValueError(
                f"Could not find 4 options:\n{text}"
            )

        options = {
            "A": option_lines[0],
            "B": option_lines[1],
            "C": option_lines[2],
            "D": option_lines[3]
        }

    return {
        "question": question,
        "options": options
    }

def fill_field(page, field_name, value):
    field = page.locator(
        '[role="listitem"]'
    ).filter(
        has=page.locator(
            f'[role="heading"]:has-text("{field_name}")'
        )
    ).locator('input[type="text"]')

    if field.count() == 0:
        print(f"Could not find: {field_name}")
        return False

    field.first.fill(value)
    print(f"Filled {field_name}: {value}")
    return True


with sync_playwright() as p:

    context = p.chromium.launch_persistent_context(
        "google_profile",
        headless=False
    )

    while True:

        form_url = input(
            "\nEnter Google Form link (or type 'exit'): "
        ).strip()

        if form_url.lower() == "exit":
            print("Exiting...")
            break

        if not form_url.startswith("http"):
            print("Invalid URL.")
            continue

        print(f"\nOpening form: {form_url}")

        page = context.new_page()
        page.goto(form_url)

        page.wait_for_timeout(2000)

        check_record_email(page)

        fill_field(page, "Email", EMAIL)
        fill_field(page, "Name of student", NAME)
        fill_field(page, "Roll No", ROLL_NO)
        fill_field(page, "Branch", BRANCH)


        questions = page.locator('[role="radiogroup"]')

        parsed_questions = []
        mcq_groups = []
        fallback_groups = []

        for i in range(questions.count()):

            group = questions.nth(i)

            container = group.locator(
                "xpath=ancestor::div[@role='listitem'][1]"
            )

            text = container.inner_text().strip()

            try:
                data = parse_question(text)

                # Proper MCQ
                if len(data["options"]) >= 4:

                    parsed_questions.append(data)
                    mcq_groups.append(group)

                else:
                    # AI cannot process it
                    fallback_groups.append(group)

                    print(
                        f"Question {i + 1}: "
                        f"AI cannot process → fallback option"
                    )

            except Exception as e:

                fallback_groups.append(group)

                print(
                    f"Question {i + 1}: "
                    f"Parser failed → fallback option"
                )

        print(
            f"\nFound {len(parsed_questions)} "
            f"AI-processable questions."
        )


        # Solve MCQs
   

        answers = {}

        if parsed_questions:

            try:
                answers = solve_questions(parsed_questions)

            except Exception as e:

                print(
                    f"\nAI solving failed: {e}"
                )

                answers = {}


        # Select AI answers

        for i, data in enumerate(parsed_questions):

            group = mcq_groups[i]

            answer = answers.get(i + 1)

            if answer in ("A", "B", "C", "D"):

                option_text = data["options"].get(
                    answer,
                    ""
                )

                try:

                    select_answer(
                        group,
                        answer,
                        option_text
                    )

                    print(
                        f"Question {i + 1}: "
                        f"AI Answer = {answer}"
                    )

                    continue

                except Exception as e:

                    print(
                        f"Question {i + 1}: "
                        f"AI selection failed: {e}"
                    )

            # AI failed → first option


            radios = group.locator(
                '[role="radio"]'
            )

            selected = False

            for j in range(radios.count()):

                radio = radios.nth(j)

                data_value = (
                    radio.get_attribute("data-value")
                    or ""
                ).strip()

                aria_label = (
                    radio.get_attribute("aria-label")
                    or ""
                ).strip()

                # Ignore empty radio elements
                if not data_value and not aria_label:
                    continue

                radio.locator(
                    "xpath=ancestor::label[1]"
                ).click()

                print(
                    f"Question {i + 1}: "
                    f"AI failed → selected first option"
                )

                selected = True
                break

            if not selected:
                print(
                    f"Question {i + 1}: "
                    f"No selectable option found"
                )

        # Fallback questions

        for group in fallback_groups:

            radios = group.locator(
                '[role="radio"]'
            )

            selected = False

            for j in range(radios.count()):

                radio = radios.nth(j)

                data_value = (
                    radio.get_attribute("data-value")
                    or ""
                ).strip()

                aria_label = (
                    radio.get_attribute("aria-label")
                    or ""
                ).strip()

                if not data_value and not aria_label:
                    continue

                radio.locator(
                    "xpath=ancestor::label[1]"
                ).click()

                print(
                    "Non-MCQ radio question: "
                    "selected first option"
                )

                selected = True
                break

            if not selected:
                print(
                    "Non-MCQ question: "
                    "no selectable option"
                )

        print("\nAll questions processed.")

        # Submit

        if AUTO_SUBMIT:

            submit = page.get_by_role(
                "button",
                name="Submit"
            )

            if submit.count() == 1:

                submit.click()

                print("Form submitted.")

            else:

                print("Submit button not found.")

        else:

            print(
                "Answers filled. "
                "Review before submitting."
            )

        input(
            "\nPress Enter to continue to next form..."
        )

        page.close()

    # Close browser only after "exit"
    context.close()

# with sync_playwright() as p:

#     context = p.chromium.launch_persistent_context(
#         "google_profile",
#         headless=False
#     )

#     while True:
#         form_url = input("\nEnter Google Form link (or type 'exit'): ").strip()

#         if form_url.lower() == "exit":
#             print("Exiting...")
#             break

#         if not form_url.startswith("http"):
#             print("Invalid URL.")
#             continue

#         print(f"\nOpening form: {form_url}")

#         page = context.new_page()
#         page.goto(form_url)

#         # Give the form time to load
#         page.wait_for_timeout(2000)

#         check_record_email(page)

#         fill_field(page, "Email", EMAIL)
#         fill_field(page, "Name of student", NAME)
#         fill_field(page, "Roll No", ROLL_NO)
#         fill_field(page, "Branch", BRANCH)

#         questions = page.locator('[role="radiogroup"]')

#         parsed_questions = []

#         for i in range(questions.count()):
#             group = questions.nth(i)

#             container = group.locator(
#             "xpath=ancestor::div[@role='listitem'][1]"
#         )

#             data = parse_question(container.inner_text())
#             parsed_questions.append(data)

#         print(f"\nFound {len(parsed_questions)} questions.")

#     # Validate
#         for i, q in enumerate(parsed_questions, 1):
#             if len(q["options"]) != 4:
#                 raise RuntimeError(
#                 f"Question {i} does not have exactly 4 options:\n{q}"
#             )
        

#     # Solve all questions in ONE API call
#         answers = solve_questions(parsed_questions)

#     # Select answers
#         for i in range(questions.count()):

#             group = questions.nth(i)

#             answer = answers[i + 1]

#             option_text = parsed_questions[i]["options"][answer]

#             print(f"Question {i + 1}: AI Answer: {answer}")

#             select_answer(group, answer, option_text)

#             print(f"Selected: {answer}")
#         # for i in range(questions.count()):

#         #     group = questions.nth(i)
#         #     answer = answers[i + 1]

#         #     print(f"Question {i + 1}: AI Answer: {answer}")

#         #     select_answer(group, answer)

#         #     print(f"Selected: {answer}")

#         # print("\nAll questions processed.")

#         if AUTO_SUBMIT:
#             submit = page.get_by_role("button", name="Submit")

#             if submit.count() == 1:
#                 submit.click()
#                 print("Form submitted.")
#             else:
#                 print("Submit button not found.")
#         else:
#             print("Answers filled. Review before submitting.")

#         input("\nPress Enter to continue to next form...")

#         page.close()
#     context.close()
