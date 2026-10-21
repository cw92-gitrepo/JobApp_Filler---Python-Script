"""Writer for Workday application forms.

Workday splits the resume part of an application into two steps:
  Step 1 "My Information": legal name, address, phone.
  Step 2 "My Experience":  work experience, education, skills, websites, LinkedIn.

write() fills step 1, clicks "Save and Continue", fills step 2, then stops
so you can review. It never clicks past step 2. If you start it while step 2
is already showing, it skips straight to step 2.

Email is never filled: Workday takes it from the account you logged in with.
Questions that aren't on a resume are listed in CONFIG_FIELDS; portal_writer
asks the user for them once and passes the saved answers in as `config`.

Selectors come from saved copies of real Workday pages. Workday names inputs
"<section>--<field>" (e.g. "name--legalName--firstName"). Step-2 entries get
a number from Workday's own counter ("workExperience-14--jobTitle"), so the
writer reads that prefix off each new entry instead of predicting it.
"""

from datetime import date

from playwright.sync_api import Locator, Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from resume import Education, Employment, Resume, UserPersonal
from writers.portal_writer import PortalConfig

# Answers Workday requires that aren't on a resume: {config key: question}.
CONFIG_FIELDS = {
    "source": "How did you hear about us? (as Workday words it, e.g. Indeed)",
    "previously_worked_here": "Have you previously worked for this organization? (Yes/No)",
    "skills": "Skills as Workday words them, comma-separated (blank or 'skip' = use your resume's):",
    "degrees": "Degree for each school in resume order as Workday words it, e.g. BS, AS"
    " (blank or 'skip' = use your resume's):",
}

MY_INFORMATION_PAGE = "[data-automation-id='applyFlowMyInfoPage']"
MY_EXPERIENCE_PAGE = "[data-automation-id='applyFlowMyExpPage']"
NEXT_BUTTON = "[data-automation-id='pageFooterNextButton']"  # "Save and Continue"

OPTION_WAIT_MS = 5_000  # how long to wait for a search result before skipping it


def write(page: Page, resume: Resume, config: PortalConfig) -> None:
    if page.locator(MY_INFORMATION_PAGE).is_visible():
        print("Workday: filling My Information")
        _fill_my_information(page, resume.personal)
        _answer_questions(page, config)
        page.locator(NEXT_BUTTON).click()

    else:
        print("Workday: My Information isn't showing, starting at My Experience")

    page.locator(MY_EXPERIENCE_PAGE).wait_for()  # waits for step 2 to render
    print("Workday: filling My Experience")
    _fill_my_experience(page, resume, config)


# --- step 1: My Information --------------------------------------------------


def _fill_my_information(page: Page, personal: UserPersonal) -> None:
    _fill(page, "name--legalName--firstName", personal.first)
    _fill(page, "name--legalName--lastName", personal.last)
    _fill(page, "address--addressLine1", personal.street)
    _fill(page, "address--city", personal.city)
    _choose(page, "address--countryRegion", personal.state)  # "State" dropdown
    _fill(page, "address--postalCode", personal.zip_code)
    _fill(page, "phoneNumber--phoneNumber", personal.phone)
    # Country is left alone: it defaults to your account's country, and
    # changing it makes Workday rebuild the whole address section.


def _answer_questions(page: Page, config: PortalConfig) -> None:
    _search_and_pick(page, "source--source", config.get("source"))
    previously_worked = config.get("previously_worked_here")
    if previously_worked is not None:
        # Radio buttons: scope to the question, then pick the label "Yes" or "No".
        question = page.locator("[data-automation-id='formField-candidateIsPreviousWorker']")
        question.get_by_label(previously_worked.strip().capitalize(), exact=True).check()


# --- step 2: My Experience ---------------------------------------------------


def _fill_my_experience(page: Page, resume: Resume, config: PortalConfig) -> None:
    for job in resume.employment:
        prefix = _add_entry(page, "Work Experience", first_field="jobTitle")
        _fill_job(page, prefix, job)

    degrees = _config_list(config, "degrees", default=[school.degree for school in resume.education])
    for index, school in enumerate(resume.education):
        prefix = _add_entry(page, "Education", first_field="schoolName")
        degree = degrees[index] if index < len(degrees) else None  # fewer answers than schools
        _fill_school(page, prefix, school, degree)

    for skill in _config_list(config, "skills", default=resume.general.skills):
        _search_and_pick(page, "skills--skills", skill)

    for url in resume.general.websites:
        _add_website(page, url)

    _fill(page, "socialNetworkAccounts--linkedInAccount", resume.personal.linkedin)


def _fill_job(page: Page, prefix: str, job: Employment) -> None:
    _fill(page, prefix + "jobTitle", job.title)
    _fill(page, prefix + "companyName", job.employer)
    _fill(page, prefix + "location", job.location)
    if job.is_current:
        _by_id(page, prefix + "currentlyWorkHere").check()
    _type_month_year(page, prefix + "startDate", job.start_date)
    if job.end_date is not None:
        _type_month_year(page, prefix + "endDate", job.end_date)
    _fill(page, prefix + "roleDescription", "\n".join(job.responsibilities) or None)


def _fill_school(page: Page, prefix: str, school: Education, degree: str | None) -> None:
    _fill(page, prefix + "schoolName", school.school)
    _choose(page, prefix + "degree", degree)
    _search_and_pick(page, prefix + "fieldOfStudy", school.major, closest_ok=True)
    _fill(page, prefix + "gradeAverage", school.gpa)
    _type_year(page, prefix + "firstYearAttended", school.start_date)
    if school.end_date is not None:
        _type_year(page, prefix + "lastYearAttended", school.end_date)


def _config_list(config: PortalConfig, key: str, default: list[str]) -> list[str]:
    """A comma-separated config answer, or the resume's values if it was skipped.

    Workday only accepts its own wording ("BS", not "Bachelor's Degree"), so
    the user can give Workday-worded values once and reuse them:
      "BS, AS"        -> ["BS", "AS"]
      "" or "skip"    -> default (the resume's values)
    """
    answer = config.get(key, "").strip()
    if answer.casefold() in ("", "skip"):
        return default
    return [item.strip() for item in answer.split(",") if item.strip()]


# --- Workday widget helpers --------------------------------------------------
# Each Workday control type needs its own way of being filled. These helpers
# are the only place that knows how, so the step functions above read like
# a list of fields.


def _by_id(page: Page, element_id: str) -> Locator:
    # [id='...'] instead of #...: safe for any characters Workday puts in ids.
    return page.locator(f"[id='{element_id}']")


def _fill(page: Page, element_id: str, value: str | None) -> None:
    """Plain text box: replace its contents. Blank resume values are skipped."""
    if value is not None:
        _by_id(page, element_id).fill(value)


def _choose(page: Page, button_id: str, option: str | None) -> None:
    """Dropdown (a button that opens a list): open it, click the closest option.

    Option wording differs between companies ("Bachelor's Degree" vs
    "Bachelors"), so a value with no clear match is skipped with the list of
    real options printed, instead of stopping the whole run.
    """
    if option is None:
        return
    _by_id(page, button_id).click()
    options = page.get_by_role("option")
    try:
        # Workday shows a "Select One" placeholder first and loads the real
        # options a moment later, so wait for an option that isn't the placeholder.
        options.filter(has_not_text="Select One").first.wait_for(timeout=OPTION_WAIT_MS)
    except PlaywrightTimeoutError:
        print(f"{button_id}: the list didn't open; skipped.")
        return
    labels = [label.strip() for label in options.all_inner_texts()]
    index = _best_match(option, labels)
    if index is None:
        print(f"{button_id}: no option matches {option!r}; skipped. Options are: {labels}")
        page.keyboard.press("Escape")
        return
    options.nth(index).click()


def _best_match(wanted: str, labels: list[str]) -> int | None:
    """Index of the label that matches `wanted`, or None if there's no clear one.

    1. exact match, ignoring case and curly vs straight apostrophes
    2. otherwise, the ONLY label containing it ("Bachelor" -> "Bachelor's Degree")
    Trace: wanted="virginia", labels=["Texas", "Virginia", "West Virginia"]
      step 1 finds "Virginia" (index 1), so "West Virginia" never gets a chance.
    """
    key = _normalize(wanted)
    keys = [_normalize(label) for label in labels]
    if key in keys:
        return keys.index(key)
    partial = [i for i, label_key in enumerate(keys) if key in label_key]
    return partial[0] if len(partial) == 1 else None


def _normalize(text: str) -> str:
    return text.replace("\u2019", "'").casefold().strip()  # \u2019 is the curly ’


def _search_and_pick(page: Page, input_id: str, text: str | None, closest_ok: bool = False) -> None:
    """Search box with results (skills, field of study): type, Enter, click a result.

    Picks the result that matches `text` (see _best_match). If none matches
    and `closest_ok` is set, it takes Workday's first result, which Workday
    ranks as the closest ("Computer Science" -> "Computer and Information
    Sciences"). Otherwise the value is skipped with the results printed.
    """
    if text is None:
        return
    search_box = _by_id(page, input_id)
    search_box.fill(text)
    search_box.press("Enter")
    results = page.get_by_role("option")
    try:
        results.first.wait_for(timeout=OPTION_WAIT_MS)
    except PlaywrightTimeoutError:
        print(f"{input_id}: Workday found nothing for {text!r}; skipped.")
        search_box.press("Escape")
        return
    labels = [label.strip() for label in results.all_inner_texts()]
    index = _best_match(text, labels)
    if index is None and closest_ok:
        index = 0
        print(f"{input_id}: no exact match for {text!r}; used the closest, {labels[0]!r}.")
    if index is None:
        print(f"{input_id}: no result matches {text!r}; skipped. Results were: {labels}")
        search_box.press("Escape")
        return
    results.nth(index).click()


def _add_entry(page: Page, section_title: str, first_field: str) -> str:
    """Click a section's Add button and return the new entry's id prefix.

    Trace for the Work Experience section:
      newest entry's wrapper  <div data-automation-id="formField-jobTitle"
                                   data-fkit-id="workExperience-14--jobTitle">
      removesuffix("jobTitle") -> "workExperience-14--"
    """
    # Every section has an "Add" button with the same automation id, so first
    # narrow to the section: <div role="group" aria-labelledby="Education-section">.
    # name="Add" also matches "Add Another", which the button becomes after one entry.
    section = page.get_by_role("group", name=section_title, exact=True)
    section.get_by_role("button", name="Add").click()

    # New entries go at the end, so .last is the one just added, even if your
    # profile already had entries.
    newest = section.locator(f"[data-automation-id='formField-{first_field}']").last
    fkit_id = newest.get_attribute("data-fkit-id") or ""
    return fkit_id.removesuffix(first_field)


def _add_website(page: Page, url: str) -> None:
    # A website entry is a single URL box, so instead of reading its id the
    # writer fills the last text box in the section: the one Add just created.
    section = page.get_by_role("group", name="Websites", exact=True)
    section.get_by_role("button", name="Add").click()
    section.locator("input[type='text']").last.fill(url)


def _type_month_year(page: Page, date_id: str, value: date) -> None:
    # Workday date fields are separate month/year boxes that react to key
    # presses, so they're typed into rather than filled.
    _type(page, f"{date_id}-dateSectionMonth-input", f"{value.month:02d}")
    _type(page, f"{date_id}-dateSectionYear-input", str(value.year))


def _type_year(page: Page, date_id: str, value: date) -> None:
    _type(page, f"{date_id}-dateSectionYear-input", str(value.year))


def _type(page: Page, element_id: str, text: str) -> None:
    # focus(), not click(): Workday keeps the real spinbutton <input> off-screen
    # and shows a "MM"/"YYYY" div in its place, so Playwright can't click it.
    # Focusing needs no on-screen position, and key presses go to the focused element.
    _by_id(page, element_id).focus()
    page.keyboard.type(text)
