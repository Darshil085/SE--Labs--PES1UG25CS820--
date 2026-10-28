\# Static Code Analysis — Reflection



\## 1. What did the static analysis tools identify?



Pylint identified code-quality and maintainability problems, including missing docstrings, inconsistent naming conventions, long lines and unsafe default arguments. Flake8 identified style violations and poor exception handling. Bandit identified security risks such as SQL injection, arbitrary code execution, weak hashing and insecure temporary-file handling.



\## 2. Which issue was the most serious, and why?



The use of `exec()` with user-controlled input was particularly serious because it could allow arbitrary code execution. SQL injection was also serious because it could alter database queries and expose customer information. These issues demonstrate why input validation and safe API usage are essential.



\## 3. How were the issues fixed?



SQL queries were changed to use parameterized statements. The promo system now accepts predefined promo codes instead of executable strings. SHA-1 was replaced with SHA-256 in the demonstration. Temporary receipt creation was made safer, file permissions were restricted, and administrator authentication no longer relies on a password hardcoded in the source. Additional checks were added for rental dates, prices and car availability.



\## 4. What did you learn from this exercise?



I learned that a program can run successfully and still contain security vulnerabilities and maintainability problems. Static analysis tools help detect these issues before deployment. Using multiple tools provides complementary perspectives: Pylint focuses on code quality, Flake8 on style, and Bandit on common security risks. I also learned that analysis results must be reviewed and followed by functional testing.



