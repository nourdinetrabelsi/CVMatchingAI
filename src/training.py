"""Curated learning references, not live course search."""
COURSES = {
 'python': ('Python', 'https://docs.python.org/3/tutorial/', 'Analyser un jeu de données avec Python.'),
 'sql': ('SQL', 'https://www.postgresql.org/docs/current/tutorial.html', 'Créer une base et écrire 10 requêtes métier.'),
 'docker': ('Docker', 'https://docs.docker.com/get-started/', 'Conteneuriser une API Python.'),
 'aws': ('AWS', 'https://skillbuilder.aws/', 'Découvrir les services cloud et leurs coûts.'),
 'tensorflow': ('TensorFlow', 'https://www.tensorflow.org/tutorials', 'Entraîner un petit modèle supervisé.'),
 'pytorch': ('PyTorch', 'https://pytorch.org/tutorials/', 'Entraîner et évaluer un réseau neuronal.'),
 'nlp': ('NLP', 'https://huggingface.co/learn/nlp-course/chapter1/1', 'Construire un classificateur de textes.'),
 'machine learning': ('Machine Learning', 'https://scikit-learn.org/stable/tutorial/index.html', 'Comparer des modèles par validation croisée.'),
 'git': ('Git', 'https://git-scm.com/book/en/v2', 'Versionner et documenter un projet.'),
 'javascript': ('JavaScript', 'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide', 'Créer une interface interactive.'),
 'excel': ('Excel', 'https://support.microsoft.com/en-us/excel', 'Construire un tableau de bord.'),
 'power bi': ('Power BI', 'https://learn.microsoft.com/en-us/training/powerplatform/power-bi', 'Construire un tableau de bord de données.'),
 'react': ('React', 'https://react.dev/learn', 'Créer une application web avec composants.'),
 'fastapi': ('FastAPI', 'https://fastapi.tiangolo.com/tutorial/', 'Créer une API REST documentée.'),
}

def recommend(skills):
    return [(skill, *COURSES[skill.lower()]) for skill in skills if skill.lower() in COURSES]
