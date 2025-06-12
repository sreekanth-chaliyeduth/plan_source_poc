# PlanSource UI Automation Framework - POC

## 1  What this does
End-to-end UI automation of the PlanSource benefits flow:

1. Create an employee  
2. Add a domestic-partner dependent  
3. Enrol both in Medical and Voluntary-Employee Life

*(Dental enrolment via API and PDF confirmation were planned but paused because of server instability and time.)*

---

## 2  Why it isn't 100 % green yet
* Yesterday the test site began throwing server errors.  
* React re-mounts swap element IDs during animations.  
* Some elements are hidden by transient overlays, so clicks miss.  
* Plan options change with location / salary; Faker data sometimes hits an invalid combo.

The suite copes with most of that, but the run can still wobble.

---

## 3  Folder map
```

plane\_source/
├─ pages/               # Page Objects
│  ├─ base\_page.py
│  ├─ login\_page.py
│  ├─ home\_page.py
│  ├─ employee\_form\_page.py
│  └─ enrollment\_wizard.py
├─ tests/
│  └─ test\_happy\_path.py
├─ [poc\_single.py](https://github.com/sreekanth-chaliyeduth/plan_source_poc/blob/main/poc_single.py)        # scratch POC from Tuesday
├─ requirements.txt
├─ pytest.ini
├─ .env.example
└─ reports/             # HTML reports land here

````

---

## 4  Quick start

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env           # put real creds in .env
pytest --html=reports/run.html --self-contained-html
open reports/run.html          # macOS; use start … on Windows
```

---

## 5  Data strategy (Faker)

* Adult-only data (18+).
* Valid US addresses / SSNs.
* Dependent age ±2 yrs of employee.
* Salaries $40k – $150k, locations SCA / NCA / NONCA.

This keeps the form happy, but random data can still trip plan-eligibility rules.

---

## 6  What's still on the backlog

* API enrolment for Dental (Swagger pending).
* PDF confirmation parsing.
* Smarter test-data generator that respects eligibility logic.
* Automatic retries around flaky nav hops.
* Parallel execution + CI matrix.
* Visual regression and basic perf hooks.

---

Thanks for the opportunity.
Happy to tighten the flow and add the API/PDF pieces once the test server stabilises or if more time opens up.

```
