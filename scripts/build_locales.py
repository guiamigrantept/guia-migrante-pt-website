#!/usr/bin/env python3
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
SOURCE_CFG = ROOT / "monitor" / "sources.json"
BASE = "https://guia-migrante-pt.pages.dev"
REVIEW_DATE = "20/08/2026"
REVIEW_ISO = "2026-08-20"

CORE_PAGES = [
    "index.html", "percursos.html", "legalizacao.html", "dia-a-dia.html",
    "nacionalidade.html", "ferramentas.html", "contactos.html", "faq.html",
    "seguranca.html",
]

COMMON = {
    "fr": {
        "lang": "fr", "name": "Français", "status": "Version française en préparation",
        "independent": "Information indépendante · Vérifiée à partir de sources officielles",
        "checked": f"Vérifié le {REVIEW_DATE}",
        "brand_sub": "Information · Orientation · Confiance",
        "nav": {
            "index.html": "Accueil", "percursos.html": "Parcours", "legalizacao.html": "Séjour / AIMA",
            "dia-a-dia.html": "Vie quotidienne", "nacionalidade.html": "Nationalité",
            "ferramentas.html": "Outils", "contactos.html": "Contacts", "faq.html": "FAQ",
            "seguranca.html": "Éviter les arnaques",
        },
        "skip": "Aller au contenu principal", "menu": "Ouvrir le menu", "language": "Langue",
        "stage": "Traduction en cours — cette version n’est pas encore proposée dans le sélecteur public tant que toutes les pages n’ont pas été relues.",
        "source": "Source officielle ↗", "official": "Sources officielles",
        "footer_note": "Portail indépendant et gratuit d’information et d’orientation pour les personnes migrantes au Portugal.",
        "legal": "Guia Migrante PT n’appartient pas à l’AIMA, au Gouvernement portugais, à l’Autorité fiscale, à la Sécurité sociale, au SNS ni à aucun autre organisme public. En cas de divergence, la législation en vigueur et l’information de l’autorité compétente prévalent.",
    },
    "es": {
        "lang": "es", "name": "Español", "status": "Versión española en preparación",
        "independent": "Información independiente · Verificada con fuentes oficiales",
        "checked": f"Verificado el {REVIEW_DATE}",
        "brand_sub": "Información · Orientación · Confianza",
        "nav": {
            "index.html": "Inicio", "percursos.html": "Rutas", "legalizacao.html": "Residencia / AIMA",
            "dia-a-dia.html": "Día a día", "nacionalidade.html": "Nacionalidad",
            "ferramentas.html": "Herramientas", "contactos.html": "Contactos", "faq.html": "Preguntas frecuentes",
            "seguranca.html": "Evitar estafas",
        },
        "skip": "Saltar al contenido principal", "menu": "Abrir menú", "language": "Idioma",
        "stage": "Traducción en curso — esta versión todavía no aparece como idioma público hasta que todas las páginas hayan sido revisadas.",
        "source": "Fuente oficial ↗", "official": "Fuentes oficiales",
        "footer_note": "Portal independiente y gratuito de información y orientación para personas migrantes en Portugal.",
        "legal": "Guia Migrante PT no pertenece ni representa a AIMA, al Gobierno de Portugal, a la Autoridad Tributaria, a la Seguridad Social, al SNS ni a ninguna otra entidad pública. En caso de divergencia, prevalecen la legislación vigente y la información de la entidad pública competente.",
    },
}

PAGES = {
"fr": {
"index.html": {
    "title": "Guia Migrante PT — Premiers pas au Portugal",
    "description": "Informations indépendantes pour les migrants au Portugal : NIF, NISS, santé, AIMA, séjour et nationalité.",
    "kicker": "Commencez ici",
    "h1": "Vos premiers pas sont plus simples quand vous savez par où commencer.",
    "lead": "Informations claires sur le NIF, le NISS, la santé, l’AIMA, le séjour et la nationalité portugaise — organisées pour trouver rapidement la bonne démarche.",
    "sections": [
        ("Choisissez votre situation", "Vous n’avez pas besoin de connaître le nom de l’administration. Commencez par votre besoin.", [
            ("Je viens d’arriver", "NIF, NISS, numéro d’usager du SNS et premières démarches pratiques.", "dia-a-dia.html"),
            ("Séjour / AIMA", "Première autorisation, renouvellement, travail, études, famille et situations transitoires.", "legalizacao.html"),
            ("Nationalité portugaise", "Résidence, mariage, ascendance et autres voies ont des conditions différentes.", "nacionalidade.html"),
            ("J’ai besoin d’aide", "Contacts AIMA, CLAIM, services consulaires et numéros d’urgence.", "contactos.html"),
        ]),
        ("Les quatre premiers repères", "Ordre pratique uniquement : votre situation juridique peut imposer un autre ordre.", [
            ("NIF", "Le numéro fiscal est utilisé pour de nombreuses démarches quotidiennes, notamment contrats et banque.", "dia-a-dia.html#nif"),
            ("NISS", "Le numéro de Sécurité sociale est lié aux cotisations et à de nombreuses démarches professionnelles.", "dia-a-dia.html#niss"),
            ("SNS", "Le numéro d’usager peut être attribué lors du premier accès à une unité publique de santé.", "dia-a-dia.html#sns"),
            ("AIMA", "Confirmez la voie de séjour correspondant à votre visa, nationalité, travail, études ou famille.", "legalizacao.html"),
        ]),
    ],
},
"percursos.html": {
    "title": "Parcours de migration et de séjour | Guia Migrante PT",
    "description": "Principaux parcours de séjour au Portugal, organisés par profil.",
    "kicker": "Tous les parcours", "h1": "Trouvez le parcours qui correspond à votre situation.",
    "lead": "Le bon point de départ dépend de votre nationalité, de l’endroit où vous vous trouvez et du motif réel de votre séjour.",
    "sections": [
        ("Par profil", "Choisissez la situation la plus proche de la vôtre. Un même document ne s’applique pas à tout le monde.", [
            ("UE / EEE / Suisse et famille", "La libre circulation suit un régime différent de celui des ressortissants de pays tiers.", "legalizacao.html"),
            ("Ressortissant CPLP", "La voie CPLP a ses propres règles de visa, de titre et de renouvellement.", "legalizacao.html"),
            ("Travail, études ou activité indépendante", "Contrat de travail, études, travail indépendant et activité hautement qualifiée sont des voies distinctes.", "legalizacao.html"),
            ("Famille", "La procédure dépend de la nationalité de la personne de référence et de la situation du membre de famille.", "legalizacao.html"),
            ("Asile / protection", "La protection internationale n’est pas un visa de travail ni une autorisation de séjour ordinaire.", "contactos.html"),
            ("Je ne sais pas quelle voie choisir", "Utilisez les informations de séjour et, si nécessaire, demandez une orientation présentielle au réseau CLAIM.", "contactos.html"),
        ]),
    ],
},
"legalizacao.html": {
    "title": "Séjour, AIMA et régularisation | Guia Migrante PT",
    "description": "Orientation indépendante sur les principales voies de séjour, renouvellements et contacts AIMA au Portugal.",
    "kicker": "Séjour et AIMA", "h1": "Ne confondez pas première autorisation, renouvellement et changement de situation.",
    "lead": "La démarche correcte dépend de votre visa, base légale, nationalité, travail, études ou famille. Vérifiez toujours le canal officiel applicable à votre cas.",
    "sections": [
        ("Points essentiels", "Avant de payer ou d’envoyer des documents, identifiez la procédure exacte.", [
            ("Première autorisation", "Une première autorisation de séjour n’est pas une simple rénovation d’un titre existant.", None),
            ("Renouvellement", "Le canal de renouvellement peut changer selon le type de titre et les fenêtres ouvertes par l’AIMA.", None),
            ("Formulaire de contact AIMA", "L’AIMA utilise son formulaire de contact pour plusieurs demandes d’orientation et de rendez-vous en présentiel.", "contactos.html"),
            ("Manifestation d’intérêt", "Les nouvelles demandes au titre de l’ancien mécanisme ont été supprimées à partir du 4 juin 2024. Les procédures antérieures et certains cas transitoires suivent des règles propres.", None),
        ]),
        ("Avant d’agir", "Les frais, documents et délais peuvent être modifiés. Une liste trouvée sur les réseaux sociaux ne remplace pas la source officielle.", [
            ("Frais AIMA", "Il n’existe pas un prix unique pour toutes les procédures. Vérifiez la table officielle applicable à votre démarche.", None),
            ("Rendez-vous", "Méfiez-vous des personnes qui vendent un rendez-vous prétendument “garanti”.", "seguranca.html"),
        ]),
    ],
},
"dia-a-dia.html": {
    "title": "NIF, NISS et SNS | Guia Migrante PT",
    "description": "Premières démarches pratiques au Portugal : NIF, NISS, numéro d’usager du SNS et services officiels.",
    "kicker": "Vie quotidienne", "h1": "NIF, NISS et santé : trois numéros différents, trois fonctions différentes.",
    "lead": "Ces démarches sont souvent parmi les premières à effectuer au Portugal, mais elles ne remplacent pas votre procédure de séjour.",
    "sections": [
        ("NIF", "Numéro d’identification fiscale.", [
            ("À quoi sert-il ?", "Il est utilisé pour les impôts et de nombreuses démarches courantes, notamment contrats et banque.", None),
            ("Coût officiel", "La demande officielle du NIF est gratuite. Un représentant privé peut facturer son propre service.", None),
        ]),
        ("NISS", "Numéro d’identification de la Sécurité sociale.", [
            ("Demande", "Les ressortissants étrangers peuvent demander le NISS en ligne lorsqu’ils remplissent les conditions applicables.", None),
            ("Utilité", "Il est utilisé pour les cotisations et les relations avec la Sécurité sociale.", None),
        ]),
        ("SNS", "Numéro national d’usager du service de santé.", [
            ("Attribution", "Pour les ressortissants étrangers, il peut être attribué lors du premier accès à une unité publique de santé.", None),
            ("Attention", "Avoir un numéro d’usager ne signifie pas automatiquement que tous les soins sont gratuits.", None),
        ]),
    ],
},
"nacionalidade.html": {
    "title": "Nationalité portugaise | Guia Migrante PT",
    "description": "Orientation sur les principales voies d’accès à la nationalité portugaise et les règles en vigueur en 2026.",
    "kicker": "Nationalité", "h1": "La nationalité portugaise dépend de la voie juridique applicable à votre situation.",
    "lead": "Résidence, mariage, filiation et autres voies ont des conditions distinctes. Ne comptez pas seulement les années : vérifiez la règle applicable à votre demande.",
    "sections": [
        ("Naturalisation par résidence — demandes nouvelles", "La loi organique entrée en vigueur le 19 mai 2026 a modifié les durées pour les nouvelles demandes d’adultes.", [
            ("7 ans", "Pour les ressortissants de pays de langue officielle portugaise et les citoyens de l’Union européenne, sous réserve des autres conditions légales.", None),
            ("10 ans", "Pour les autres ressortissants, sous réserve des autres conditions légales.", None),
            ("Demandes déjà pendantes", "Les demandes introduites avant l’entrée en vigueur de la nouvelle loi conservent le régime antérieur selon les règles transitoires.", None),
        ]),
        ("Autres voies", "La résidence n’est pas la seule possibilité.", [
            ("Fils, petit-fils ou autre descendance", "Les règles varient selon le lien familial, la preuve de filiation et les conditions propres à chaque voie.", None),
            ("Mariage ou union de fait", "Il existe une voie spécifique, avec des conditions et preuves propres.", None),
        ]),
    ],
},
"ferramentas.html": {
    "title": "Outils gratuits | Guia Migrante PT",
    "description": "Outils gratuits pour organiser les démarches de migration et de vie au Portugal.",
    "kicker": "Outils", "h1": "Organisez vos démarches sans envoyer de documents sensibles au Guia.",
    "lead": "Les outils publics du Guia servent à organiser des étapes, créer des check-lists et comprendre quel service rechercher. Ils ne décident pas de votre éligibilité juridique.",
    "sections": [
        ("Outils prévus dans cette traduction", "L’interface interactive française sera activée après validation complète de la traduction.", [
            ("Parcours personnalisé", "Ordonne les prochaines étapes selon votre objectif général.", None),
            ("Check-list de premiers pas", "Permet de suivre NIF, NISS, SNS et autres démarches dans votre navigateur.", None),
            ("Validité des documents", "Compte les jours jusqu’à une date saisie, sans calculer un délai juridique de renouvellement.", None),
            ("Quel service chercher ?", "Aide à distinguer AIMA, Finanças, Sécurité sociale, SNS, Justice, CLAIM et consulat.", None),
        ]),
    ],
},
"contactos.html": {
    "title": "Contacts utiles au Portugal | Guia Migrante PT",
    "description": "AIMA, CLAIM, consulats et numéros utiles pour les migrants au Portugal.",
    "kicker": "Contacts", "h1": "Utilisez le canal officiel correspondant au problème que vous devez résoudre.",
    "lead": "Le Guia n’accède pas à votre dossier individuel. Pour une décision, un rendez-vous ou un document officiel, utilisez l’entité compétente.",
    "sections": [
        ("Où chercher de l’aide", "Quelques points de départ sûrs.", [
            ("AIMA", "Séjour, titres, plusieurs rendez-vous et questions migratoires relevant de l’AIMA.", None),
            ("Réseau CLAIM", "Orientation locale gratuite et accompagnement de proximité pour les personnes migrantes.", None),
            ("Consulat", "Passeport, actes ou démarches qui relèvent de votre pays d’origine.", None),
            ("Urgence", "En danger immédiat au Portugal, appelez le 112.", None),
        ]),
    ],
},
"faq.html": {
    "title": "Questions fréquentes | Guia Migrante PT",
    "description": "Réponses rapides sur NIF, NISS, AIMA, séjour, nationalité, sécurité et outils.",
    "kicker": "FAQ", "h1": "Réponses rapides aux questions les plus fréquentes.",
    "lead": "Ces réponses orientent vers la bonne information. Elles ne remplacent pas une décision de l’autorité compétente.",
    "faqs": [
        ("Le Guia peut-il savoir si mon titre sera approuvé ?", "Non. Le Guia explique les règles et les démarches mais n’accède pas aux dossiers individuels et ne peut garantir une décision."),
        ("NIF, NISS et numéro d’usager SNS sont-ils la même chose ?", "Non. Le NIF est fiscal, le NISS relève de la Sécurité sociale et le numéro d’usager concerne le système de santé."),
        ("Dois-je payer quelqu’un pour obtenir un rendez-vous AIMA ?", "Méfiez-vous des rendez-vous prétendument garantis. Vérifiez toujours les canaux et frais officiels avant de payer."),
        ("Le compteur de validité calcule-t-il mon délai légal de renouvellement ?", "Non. Il compte seulement les jours par rapport à la date que vous saisissez."),
        ("Ai-je besoin d’un compte pour utiliser le Guia ?", "Non. Les informations et outils publics sont accessibles sans compte."),
    ],
},
"seguranca.html": {
    "title": "Éviter les arnaques | Guia Migrante PT",
    "description": "Conseils pratiques pour reconnaître les arnaques liées aux rendez-vous, documents, paiements et démarches migratoires.",
    "kicker": "Sécurité", "h1": "Urgence, peur et promesses de résultat sont souvent utilisées pour vous faire payer trop vite.",
    "lead": "Vérifiez le domaine, les frais officiels et l’identité de la personne avant d’envoyer de l’argent, des documents ou des codes d’accès.",
    "sections": [
        ("Signaux d’alerte", "Arrêtez-vous et vérifiez avant d’agir.", [
            ("“Rendez-vous AIMA exclusif”", "Une personne privée ne peut pas garantir un rendez-vous ou une décision favorable d’une autorité publique.", None),
            ("Demande de mots de passe ou codes SMS", "Ne partagez jamais vos mots de passe, PIN, codes d’authentification ou codes reçus par SMS.", None),
            ("“Payez maintenant ou vous perdez votre dossier”", "Les messages qui créent une urgence artificielle doivent être vérifiés directement auprès de la source officielle.", None),
            ("Site presque identique à un site public", "Vérifiez soigneusement le domaine avant de saisir des données personnelles ou bancaires.", None),
        ]),
    ],
},
},
"es": {
"index.html": {
    "title": "Guia Migrante PT — Primeros pasos en Portugal",
    "description": "Información independiente para migrantes en Portugal: NIF, NISS, salud, AIMA, residencia y nacionalidad.",
    "kicker": "Empieza aquí", "h1": "Los primeros pasos son más sencillos cuando sabes por dónde empezar.",
    "lead": "Información clara sobre NIF, NISS, salud, AIMA, residencia y nacionalidad portuguesa, organizada para encontrar rápidamente el trámite correcto.",
    "sections": [
        ("Elige tu situación", "No necesitas saber qué organismo es responsable. Empieza por lo que necesitas resolver.", [
            ("Acabo de llegar", "NIF, NISS, número de usuario del SNS y primeros pasos prácticos.", "dia-a-dia.html"),
            ("Residencia / AIMA", "Primera autorización, renovación, trabajo, estudios, familia y situaciones transitorias.", "legalizacao.html"),
            ("Nacionalidad portuguesa", "Residencia, matrimonio, ascendencia y otras vías tienen requisitos diferentes.", "nacionalidade.html"),
            ("Necesito ayuda", "Contactos de AIMA, CLAIM, consulados y números de emergencia.", "contactos.html"),
        ]),
        ("Cuatro referencias iniciales", "Es un orden práctico, no un calendario legal obligatorio.", [
            ("NIF", "El número fiscal se utiliza en muchos trámites cotidianos, incluidos contratos y banca.", "dia-a-dia.html#nif"),
            ("NISS", "El número de la Seguridad Social está relacionado con cotizaciones y muchos trámites laborales.", "dia-a-dia.html#niss"),
            ("SNS", "El número de usuario puede asignarse al acceder por primera vez a una unidad pública de salud.", "dia-a-dia.html#sns"),
            ("AIMA", "Confirma la vía de residencia correspondiente a tu visado, nacionalidad, trabajo, estudios o familia.", "legalizacao.html"),
        ]),
    ],
},
"percursos.html": {
    "title": "Rutas migratorias y de residencia | Guia Migrante PT",
    "description": "Principales rutas de residencia en Portugal organizadas por perfil.",
    "kicker": "Todas las rutas", "h1": "Encuentra la ruta que encaja con tu situación.",
    "lead": "El punto de partida correcto depende de tu nacionalidad, de dónde te encuentras y del objetivo real de tu estancia.",
    "sections": [
        ("Por perfil", "Elige la situación más parecida a la tuya. No existe un único procedimiento para todas las personas migrantes.", [
            ("UE / EEE / Suiza y familiares", "La libre circulación sigue un régimen distinto del de nacionales de terceros países.", "legalizacao.html"),
            ("Nacional de la CPLP", "La vía CPLP tiene reglas propias sobre visado, tarjeta y renovación.", "legalizacao.html"),
            ("Trabajo, estudios o actividad independiente", "Empleo, estudios, trabajo por cuenta propia y actividad altamente cualificada son vías distintas.", "legalizacao.html"),
            ("Familia", "El procedimiento depende de la nacionalidad y del derecho de residencia de la persona de referencia.", "legalizacao.html"),
            ("Asilo / protección", "La protección internacional no es un visado laboral ni una autorización ordinaria de residencia.", "contactos.html"),
            ("No sé qué vía elegir", "Consulta la información de residencia y, si es necesario, busca orientación presencial en la red CLAIM.", "contactos.html"),
        ]),
    ],
},
"legalizacao.html": {
    "title": "Residencia, AIMA y regularización | Guia Migrante PT",
    "description": "Orientación independiente sobre vías de residencia, renovaciones y contactos de AIMA en Portugal.",
    "kicker": "Residencia y AIMA", "h1": "No confundas una primera autorización, una renovación y un cambio de situación.",
    "lead": "El trámite correcto depende del visado, base legal, nacionalidad, trabajo, estudios o familia. Comprueba siempre el canal oficial aplicable a tu caso.",
    "sections": [
        ("Puntos esenciales", "Antes de pagar o enviar documentos, identifica el procedimiento exacto.", [
            ("Primera autorización", "Una primera autorización de residencia no es una simple renovación de una tarjeta ya existente.", None),
            ("Renovación", "El canal de renovación puede cambiar según el tipo de título y las ventanas abiertas por AIMA.", None),
            ("Formulario de contacto de AIMA", "AIMA utiliza su formulario de contacto para varias solicitudes de orientación y citas presenciales.", "contactos.html"),
            ("Manifestación de interés", "Las nuevas solicitudes por el antiguo mecanismo dejaron de admitirse desde el 4 de junio de 2024. Los procedimientos anteriores y determinados casos transitorios tienen reglas propias.", None),
        ]),
        ("Antes de actuar", "Las tasas, documentos y plazos pueden cambiar. Una lista de redes sociales no sustituye a la fuente oficial.", [
            ("Tasas de AIMA", "No existe un precio único para todos los procedimientos. Comprueba la tabla oficial aplicable a tu trámite.", None),
            ("Citas", "Desconfía de quien venda una cita supuestamente garantizada.", "seguranca.html"),
        ]),
    ],
},
"dia-a-dia.html": {
    "title": "NIF, NISS y SNS | Guia Migrante PT",
    "description": "Primeros trámites prácticos en Portugal: NIF, NISS, número de usuario del SNS y servicios oficiales.",
    "kicker": "Día a día", "h1": "NIF, NISS y salud: tres números diferentes con funciones diferentes.",
    "lead": "Suelen ser algunos de los primeros trámites en Portugal, pero no sustituyen a tu procedimiento de residencia.",
    "sections": [
        ("NIF", "Número de Identificación Fiscal.", [
            ("¿Para qué sirve?", "Se utiliza para impuestos y muchos trámites cotidianos, incluidos contratos y banca.", None),
            ("Coste oficial", "La solicitud oficial del NIF es gratuita. Un representante privado puede cobrar por su propio servicio.", None),
        ]),
        ("NISS", "Número de Identificación de la Seguridad Social.", [
            ("Solicitud", "Las personas extranjeras pueden solicitar el NISS por internet cuando se cumplen las condiciones aplicables.", None),
            ("Utilidad", "Se utiliza para cotizaciones y relaciones con la Seguridad Social.", None),
        ]),
        ("SNS", "Número nacional de usuario del sistema público de salud.", [
            ("Asignación", "Para personas extranjeras puede asignarse en el primer acceso a una unidad pública de salud.", None),
            ("Atención", "Tener número de usuario no significa automáticamente que todos los cuidados sean gratuitos.", None),
        ]),
    ],
},
"nacionalidade.html": {
    "title": "Nacionalidad portuguesa | Guia Migrante PT",
    "description": "Orientación sobre las principales vías de nacionalidad portuguesa y las reglas vigentes en 2026.",
    "kicker": "Nacionalidad", "h1": "La nacionalidad portuguesa depende de la vía jurídica aplicable a tu situación.",
    "lead": "Residencia, matrimonio, ascendencia y otras vías tienen requisitos distintos. No cuentes solo los años: comprueba la norma aplicable a tu solicitud.",
    "sections": [
        ("Naturalización por residencia — nuevas solicitudes", "La Ley Orgánica que entró en vigor el 19 de mayo de 2026 modificó los periodos para nuevas solicitudes de adultos.", [
            ("7 años", "Para nacionales de países de lengua oficial portuguesa y ciudadanos de la Unión Europea, además de los demás requisitos legales.", None),
            ("10 años", "Para las demás nacionalidades, además de los demás requisitos legales.", None),
            ("Solicitudes ya pendientes", "Las solicitudes presentadas antes de la entrada en vigor de la nueva ley mantienen el régimen anterior conforme a las reglas transitorias.", None),
        ]),
        ("Otras vías", "La residencia no es la única posibilidad.", [
            ("Hijo, nieto u otra descendencia", "Las reglas varían según el vínculo familiar, la prueba de filiación y los requisitos de cada vía.", None),
            ("Matrimonio o unión de hecho", "Existe una vía específica con requisitos y pruebas propias.", None),
        ]),
    ],
},
"ferramentas.html": {
    "title": "Herramientas gratuitas | Guia Migrante PT",
    "description": "Herramientas gratuitas para organizar trámites migratorios y de vida en Portugal.",
    "kicker": "Herramientas", "h1": "Organiza tus trámites sin enviar documentos sensibles al Guia.",
    "lead": "Las herramientas públicas sirven para ordenar pasos, crear listas y entender qué servicio buscar. No deciden tu elegibilidad jurídica.",
    "sections": [
        ("Herramientas previstas en esta traducción", "La interfaz interactiva en español se activará después de revisar toda la traducción.", [
            ("Ruta personalizada", "Ordena los próximos pasos según tu objetivo general.", None),
            ("Lista de primeros pasos", "Permite seguir NIF, NISS, SNS y otros trámites en tu navegador.", None),
            ("Validez de documentos", "Cuenta días respecto a una fecha introducida, sin calcular un plazo jurídico de renovación.", None),
            ("¿Qué servicio debo buscar?", "Ayuda a distinguir AIMA, Finanças, Seguridad Social, SNS, Justicia, CLAIM y consulado.", None),
        ]),
    ],
},
"contactos.html": {
    "title": "Contactos útiles en Portugal | Guia Migrante PT",
    "description": "AIMA, CLAIM, consulados y números útiles para migrantes en Portugal.",
    "kicker": "Contactos", "h1": "Usa el canal oficial correspondiente al problema que necesitas resolver.",
    "lead": "El Guia no accede a expedientes individuales. Para una decisión, cita o documento oficial, utiliza la entidad competente.",
    "sections": [
        ("Dónde buscar ayuda", "Puntos de partida seguros.", [
            ("AIMA", "Residencia, títulos, varias citas y cuestiones migratorias que dependen de AIMA.", None),
            ("Red CLAIM", "Orientación local gratuita y apoyo de proximidad para personas migrantes.", None),
            ("Consulado", "Pasaporte, certificados o trámites que dependen de tu país de origen.", None),
            ("Emergencia", "Si existe peligro inmediato en Portugal, llama al 112.", None),
        ]),
    ],
},
"faq.html": {
    "title": "Preguntas frecuentes | Guia Migrante PT",
    "description": "Respuestas rápidas sobre NIF, NISS, AIMA, residencia, nacionalidad, seguridad y herramientas.",
    "kicker": "Preguntas frecuentes", "h1": "Respuestas rápidas a las dudas más comunes.",
    "lead": "Estas respuestas orientan hacia la información correcta. No sustituyen una decisión del organismo competente.",
    "faqs": [
        ("¿El Guia puede saber si aprobarán mi residencia?", "No. El Guia explica reglas y procedimientos, pero no accede a expedientes individuales ni puede garantizar una decisión."),
        ("¿NIF, NISS y número de usuario del SNS son lo mismo?", "No. El NIF es fiscal, el NISS corresponde a la Seguridad Social y el número de usuario pertenece al sistema de salud."),
        ("¿Tengo que pagar a alguien para conseguir una cita de AIMA?", "Desconfía de las citas supuestamente garantizadas. Comprueba siempre los canales y tasas oficiales antes de pagar."),
        ("¿El contador de validez calcula mi plazo legal de renovación?", "No. Solo cuenta días respecto a la fecha que introduces."),
        ("¿Necesito una cuenta para usar el Guia?", "No. La información y las herramientas públicas están disponibles sin cuenta."),
    ],
},
"seguranca.html": {
    "title": "Evitar estafas | Guia Migrante PT",
    "description": "Consejos para reconocer estafas relacionadas con citas, documentos, pagos y trámites migratorios.",
    "kicker": "Seguridad", "h1": "La urgencia, el miedo y las promesas de resultado se utilizan para hacerte pagar demasiado rápido.",
    "lead": "Comprueba el dominio, las tasas oficiales y la identidad de quien te contacta antes de enviar dinero, documentos o códigos de acceso.",
    "sections": [
        ("Señales de alerta", "Detente y comprueba antes de actuar.", [
            ("“Cita exclusiva de AIMA”", "Una persona privada no puede garantizar una cita ni una decisión favorable de una entidad pública.", None),
            ("Solicitud de contraseñas o códigos SMS", "No compartas contraseñas, PIN, códigos de autenticación ni códigos recibidos por SMS.", None),
            ("“Paga ahora o pierdes tu proceso”", "Los mensajes que crean una urgencia artificial deben verificarse directamente en la fuente oficial.", None),
            ("Web casi idéntica a una página pública", "Comprueba cuidadosamente el dominio antes de introducir datos personales o bancarios.", None),
        ]),
    ],
},
},
}

OFFICIAL_LINKS = {
    "nif": "https://www.gov.pt/servicos/pedir-o-numero-de-identificacao-fiscal-para-pessoa-singular",
    "niss": "https://www.gov.pt/servicos/pedir-o-numero-de-identificacao-da-seguranca-social-niss-",
    "sns": "https://www.gov.pt/servicos/pedir-o-numero-de-utente-do-sns",
    "aima": "https://aima.gov.pt/",
    "justice": "https://justica.gov.pt/",
    "social": "https://www.seg-social.pt/",
}


def load_source_ids(page: str) -> list[str]:
    if not SOURCE_CFG.exists():
        return []
    try:
        data = json.loads(SOURCE_CFG.read_text(encoding="utf-8"))
    except Exception:
        return []
    ids = []
    for src in data.get("sources", []):
        pages = set(src.get("pages", []))
        if page in pages or f"en/{page}" in pages:
            ids.append(src.get("id"))
    return sorted(x for x in ids if x)


def cards(items, source_label):
    out = ['<div class="grid two">']
    for title, text, href in items:
        out.append('<article class="card">')
        out.append(f'<h3>{html.escape(title)}</h3><p>{html.escape(text)}</p>')
        if href:
            out.append(f'<a class="inline" href="{html.escape(href, quote=True)}">{html.escape(source_label if href.startswith("http") else "→")}</a>')
        out.append('</article>')
    out.append('</div>')
    return ''.join(out)


def page_html(locale: str, page: str, data: dict) -> str:
    c = COMMON[locale]
    nav = c["nav"]
    current = nav.get(page, nav["index.html"])
    alternates = [
        f'<link rel="alternate" hreflang="pt-PT" href="{BASE}/{page}">',
        f'<link rel="alternate" hreflang="en" href="{BASE}/en/{page}">',
    ]
    source_ids = load_source_ids(page)
    source_meta = f'<meta name="official-source-ids" content="{html.escape(" ".join(source_ids))}">' if source_ids else ""
    nav_html = ''.join(
        f'<a href="{p}"{(" aria-current=\"page\"" if p == page else "")}>{html.escape(label)}</a>'
        for p, label in nav.items()
    )
    mobile_html = ''.join(f'<a href="{p}">{html.escape(label)}</a>' for p, label in nav.items())
    sections_html = []
    if "sections" in data:
        for title, intro, items in data["sections"]:
            section_id = ""
            if page == "dia-a-dia.html":
                low = title.lower()
                if low == "nif": section_id = ' id="nif"'
                elif low == "niss": section_id = ' id="niss"'
                elif low == "sns": section_id = ' id="sns"'
            sections_html.append(
                f'<section class="content"{section_id}><div class="container"><div class="section-head"><h2>{html.escape(title)}</h2><p>{html.escape(intro)}</p></div>{cards(items, c["source"])}</div></section>'
            )
    if "faqs" in data:
        faq = ''.join(f'<article class="faq-item"><h3>{html.escape(q)}</h3><p>{html.escape(a)}</p></article>' for q,a in data["faqs"])
        sections_html.append(f'<section class="content"><div class="container"><div class="faq-list">{faq}</div></div></section>')

    official = (
        f'<section class="content white"><div class="container"><div class="section-head"><h2>{html.escape(c["official"])}</h2>'
        f'<p>{html.escape(c["checked"])}. Confirmez toujours la page officielle avant d’agir.</p></div>' if locale == "fr" else
        f'<section class="content white"><div class="container"><div class="section-head"><h2>{html.escape(c["official"])}</h2><p>{html.escape(c["checked"])}. Comprueba siempre la página oficial antes de actuar.</p></div>'
    )
    official += '<div class="grid three">'
    for name, url in [("AIMA",OFFICIAL_LINKS["aima"]),("gov.pt","https://www.gov.pt/"),("Justiça",OFFICIAL_LINKS["justice"]),("Segurança Social",OFFICIAL_LINKS["social"])]:
        official += f'<a class="card" href="{url}" target="_blank" rel="noopener"><h3>{html.escape(name)}</h3><p>{html.escape(c["source"])}</p></a>'
    official += '</div></div></section>'

    footer_links = ''.join(f'<a href="{p}">{html.escape(label)}</a>' for p,label in list(nav.items())[:6])
    other_links = ''.join(f'<a href="{p}">{html.escape(nav[p])}</a>' for p in ["contactos.html","faq.html","seguranca.html"])

    return f'''<!doctype html>
<html lang="{locale}">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#09315c">
<meta name="description" content="{html.escape(data['description'], quote=True)}"><meta name="last-reviewed" content="{REVIEW_ISO}"><meta name="robots" content="noindex,nofollow">
<title>{html.escape(data['title'])}</title><link rel="canonical" href="{BASE}/{locale}/{page}">{''.join(alternates)}
<link rel="icon" href="../favicon.png"><link rel="stylesheet" href="../locale-core.css"><link rel="stylesheet" href="../language-switcher.css">{source_meta}
</head>
<body>
<a class="skip-link" href="#content">{html.escape(c['skip'])}</a>
<div class="topbar"><div class="container">{html.escape(c['independent'])} · {html.escape(c['checked'])}</div></div>
<header><div class="container header-inner">
<a class="brand" href="index.html" aria-label="Guia Migrante PT"><img src="../logo-guia-migrante-256.png" alt=""><span><strong>Guia Migrante PT</strong><small>{html.escape(c['brand_sub'])}</small></span></a>
<nav class="desktop-nav" aria-label="Navigation">{nav_html}</nav>
<div class="header-actions"><div class="site-lang" aria-label="{html.escape(c['language'])}"><a href="../{page}">PT</a><a href="../en/{page}">EN</a><a class="active" href="{page}">{locale.upper()}</a></div><button class="menu-btn" id="menuButton" type="button" aria-expanded="false" aria-controls="mobileNav" aria-label="{html.escape(c['menu'])}">☰</button></div>
</div><nav class="mobile-nav" id="mobileNav" aria-label="Navigation mobile">{mobile_html}</nav></header><div class="brand-stripe"></div>
<div class="review-strip"><div class="container"><span class="review-badge">{html.escape(c['status'])}</span><span>{html.escape(c['stage'])}</span></div></div>
<main id="content"><section class="hero"><div class="container"><div class="breadcrumbs">Guia Migrante PT · {html.escape(current)}</div><span class="kicker">{html.escape(data['kicker'])}</span><h1>{html.escape(data['h1'])}</h1><p>{html.escape(data['lead'])}</p><div class="hero-actions"><a class="btn primary" href="percursos.html">{html.escape(nav['percursos.html'])}</a><a class="btn secondary" href="contactos.html">{html.escape(nav['contactos.html'])}</a></div><div class="notice">{html.escape(c['stage'])}</div></div></section>{''.join(sections_html)}{official}</main>
<footer><div class="container footer-grid"><div><a class="brand" href="index.html"><img src="../logo-guia-migrante-256.png" alt=""><span><strong style="color:white">Guia Migrante PT</strong><small>{html.escape(c['brand_sub'])}</small></span></a><p class="footer-note">{html.escape(c['footer_note'])}</p></div><div><div class="footer-title">Portal</div><div class="footer-links">{footer_links}</div></div><div><div class="footer-title">{html.escape(c['official'])}</div><div class="footer-links">{other_links}</div></div></div><div class="container footer-bottom"><span>© 2026 Guia Migrante PT</span><span>{html.escape(c['legal'])}</span></div></footer>
<script>const mb=document.getElementById('menuButton'),mn=document.getElementById('mobileNav');if(mb&&mn)mb.addEventListener('click',()=>{{const o=mn.classList.toggle('open');mb.setAttribute('aria-expanded',String(o));}});</script>
<script src="../language-switcher.js" defer></script>
</body></html>'''


def build() -> None:
    for locale, pages in PAGES.items():
        target = SITE / locale
        target.mkdir(parents=True, exist_ok=True)
        for page in CORE_PAGES:
            data = pages[page]
            (target / page).write_text(page_html(locale, page, data), encoding="utf-8")
    print("Built staged FR/ES core translations:", len(CORE_PAGES) * 2, "pages")


if __name__ == "__main__":
    build()
