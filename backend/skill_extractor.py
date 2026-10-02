import re

SKILL_ALIASES = {
 "Python":["python","py"], "Java":["java"], "C":["c"], "C++":["c++","cpp"], "JavaScript":["javascript","js"], "TypeScript":["typescript","ts"], "React":["react","reactjs","react.js"], "Node.js":["node.js","nodejs","node"], "HTML":["html"], "CSS":["css"], "SQL":["sql"], "MySQL":["mysql"], "PostgreSQL":["postgresql","postgres"], "MongoDB":["mongodb","mongo"], "Git":["git"], "GitHub":["github"], "Docker":["docker"], "AWS":["aws","amazon web services"], "Kubernetes":["kubernetes","k8s"], "Machine Learning":["machine learning","ml"], "Deep Learning":["deep learning"], "Data Science":["data science"], "Artificial Intelligence":["artificial intelligence","ai"], "FastAPI":["fastapi"], "Django":["django"], "Flask":["flask"], "Spring Boot":["spring boot"], "Communication":["communication"], "Leadership":["leadership"], "Teamwork":["teamwork","team work"], "Problem Solving":["problem solving"], "Time Management":["time management"], "Adaptability":["adaptability"], "Critical Thinking":["critical thinking"] }
TECHNICAL = set(list(SKILL_ALIASES)[:26])
ATS_KEYWORDS = ["python","java","javascript","react","sql","git","docker","aws","api","agile","database","cloud","testing","project","experience"]
def has_term(text, term): return bool(re.search(r"(?<![\w+.#-])" + re.escape(term) + r"(?![\w+.#-])", text, re.I))
def extract_skills(text): return [name for name, aliases in SKILL_ALIASES.items() if any(has_term(text, a) for a in aliases)]
