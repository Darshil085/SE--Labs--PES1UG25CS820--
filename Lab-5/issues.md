\# Static Code Analysis — Issues Report



\## Project

Car Rental System



\## Tools Used

\- Pylint: Python code quality and maintainability

\- Flake8: Python style and formatting

\- Bandit: Security analysis



\## Issues Identified



\### 1. SQL Injection — High Priority

\*\*Original locations:\*\* `registerCustomer()` and `findCustomer()`



\*\*Problem:\*\* SQL queries were constructed by concatenating user-controlled input. Malicious input could alter query behaviour and expose customer records.



\*\*Fix:\*\* Replaced string-based query construction with parameterized SQL statements using placeholders.



\### 2. Arbitrary Code Execution — High Priority

\*\*Original location:\*\* `applyPromo()`



\*\*Problem:\*\* The function used `exec()` to execute a supplied string, potentially allowing arbitrary Python code to run.



\*\*Fix:\*\* Replaced executable promo rules with a predefined dictionary of approved promo codes and discount rates.



\### 3. Weak Licence Hashing — High Priority

\*\*Original location:\*\* `licenceHash()`



\*\*Problem:\*\* SHA-1 was used to generate licence hashes, which is unsuitable for modern security-sensitive hashing.



\*\*Fix:\*\* Replaced SHA-1 with SHA-256 for the demonstration. A real application should use a keyed construction or appropriate protection for sensitive licence data.



\### 4. Insecure Temporary File Creation — Medium Priority

\*\*Original location:\*\* `writeReceipt()`



\*\*Problem:\*\* The original program used `tempfile.mktemp()`, which can create a race condition between choosing a filename and opening the file.



\*\*Fix:\*\* Replaced it with `tempfile.NamedTemporaryFile()` and restricted receipt permissions where supported.



\### 5. Overly Permissive File Permissions — High Priority

\*\*Original location:\*\* `writeReceipt()`



\*\*Problem:\*\* The original code applied permissions `0o777`, potentially allowing other users to read, modify or execute the receipt.



\*\*Fix:\*\* Restricted the receipt permissions to `0o600` where supported.



\### 6. Hardcoded Administrator Credential — High Priority

\*\*Original location:\*\* `adminLogin()`



\*\*Problem:\*\* The administrator password was hardcoded in the source code.



\*\*Fix:\*\* The demonstration now reads the expected password from an environment variable and compares password-derived values using a constant-time comparison.



\### 7. Unsafe Rental Validation — Medium Priority

\*\*Original location:\*\* `rentCar()`



\*\*Problem:\*\* The original function allowed invalid date ranges, repeated bookings and negative daily rental rates.



\*\*Fix:\*\* Added date, price and availability validation.



\### 8. Inadequate Error Handling — Low Priority

\*\*Original location:\*\* `returnCar()`



\*\*Problem:\*\* A bare exception handler silently ignored errors and returned `None` for an unknown car.



\*\*Fix:\*\* Added explicit validation and meaningful `ValueError` exceptions.



\## Conclusion



The initial Pylint score was 4.94/10. After refactoring, the score improved to 9.90/10, and Bandit reported zero findings in the updated scan. Final validation should be repeated after all changes. Static analysis results do not guarantee that a program is completely secure.

