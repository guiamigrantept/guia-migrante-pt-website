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

PAGES = [
    "saude-completa.html",
    "trabalho-direitos.html",
    "habitacao.html",
    "qualificacoes.html",
    "servicos-casa.html",
    "apoios-sociais.html",
    "banco-pagamentos.html",
    "carta-conducao.html",
    "consumidor.html",
]

UI = {
    "fr": {
        "name":"Français","stage":"Traduction en cours — cette page n’est pas encore indexée ni proposée publiquement tant que la révision complète n’est pas terminée.",
        "verified":f"Vérifié le {REVIEW_DATE}","independent":"Information indépendante · Sources officielles",
        "home":"Accueil","routes":"Parcours","daily":"Vie quotidienne","contacts":"Contacts","faq":"FAQ","security":"Éviter les arnaques",
        "practical":"Points pratiques","official":"Sources officielles","check":"Vérifiez toujours la source officielle avant d’agir.",
        "legal":"Guia Migrante PT est un portail indépendant. En cas de divergence, la législation en vigueur et l’information de l’autorité compétente prévalent.",
        "source":"Source officielle ↗","menu":"Ouvrir le menu","skip":"Aller au contenu principal",
    },
    "es": {
        "name":"Español","stage":"Traducción en curso — esta página todavía no se indexa ni se ofrece públicamente hasta terminar la revisión completa.",
        "verified":f"Verificado el {REVIEW_DATE}","independent":"Información independiente · Fuentes oficiales",
        "home":"Inicio","routes":"Rutas","daily":"Día a día","contacts":"Contactos","faq":"Preguntas frecuentes","security":"Evitar estafas",
        "practical":"Puntos prácticos","official":"Fuentes oficiales","check":"Comprueba siempre la fuente oficial antes de actuar.",
        "legal":"Guia Migrante PT es un portal independiente. En caso de divergencia, prevalecen la legislación vigente y la información de la autoridad competente.",
        "source":"Fuente oficial ↗","menu":"Abrir menú","skip":"Saltar al contenido principal",
    },
    "uk": {
        "name":"Українська","stage":"Переклад триває — ця сторінка ще не індексується і не пропонується публічно до завершення повної перевірки.",
        "verified":f"Перевірено {REVIEW_DATE}","independent":"Незалежна інформація · Офіційні джерела",
        "home":"Головна","routes":"Маршрути","daily":"Щоденні справи","contacts":"Контакти","faq":"Поширені питання","security":"Уникнення шахрайства",
        "practical":"Практичні орієнтири","official":"Офіційні джерела","check":"Перед будь-якими діями завжди перевіряйте офіційне джерело.",
        "legal":"Guia Migrante PT — незалежний портал. У разі розбіжностей перевагу мають чинне законодавство та інформація компетентного органу.",
        "source":"Офіційне джерело ↗","menu":"Відкрити меню","skip":"Перейти до основного вмісту",
    },
    "ru": {
        "name":"Русский","stage":"Перевод продолжается — эта страница пока не индексируется и не предлагается публично до завершения полной проверки.",
        "verified":f"Проверено {REVIEW_DATE}","independent":"Независимая информация · Официальные источники",
        "home":"Главная","routes":"Маршруты","daily":"Повседневные вопросы","contacts":"Контакты","faq":"Частые вопросы","security":"Как избежать мошенничества",
        "practical":"Практические ориентиры","official":"Официальные источники","check":"Перед любыми действиями всегда проверяйте официальный источник.",
        "legal":"Guia Migrante PT — независимый портал. При расхождениях приоритет имеют действующее законодательство и информация компетентного органа.",
        "source":"Официальный источник ↗","menu":"Открыть меню","skip":"Перейти к основному содержанию",
    },
    "hi": {
        "name":"हिन्दी","stage":"अनुवाद जारी है — पूरी समीक्षा समाप्त होने तक यह पृष्ठ इंडेक्स या सार्वजनिक भाषा-चयन में शामिल नहीं किया जाएगा।",
        "verified":f"सत्यापित: {REVIEW_DATE}","independent":"स्वतंत्र जानकारी · आधिकारिक स्रोत",
        "home":"मुखपृष्ठ","routes":"मार्ग","daily":"दैनिक जीवन","contacts":"संपर्क","faq":"सामान्य प्रश्न","security":"धोखाधड़ी से बचें",
        "practical":"व्यावहारिक बिंदु","official":"आधिकारिक स्रोत","check":"कोई कदम उठाने से पहले हमेशा आधिकारिक स्रोत जाँचें।",
        "legal":"Guia Migrante PT एक स्वतंत्र पोर्टल है। किसी अंतर की स्थिति में लागू कानून और सक्षम प्राधिकरण की आधिकारिक जानकारी को प्राथमिकता दी जाती है।",
        "source":"आधिकारिक स्रोत ↗","menu":"मेनू खोलें","skip":"मुख्य सामग्री पर जाएँ",
    },
    "bn": {
        "name":"বাংলা","stage":"অনুবাদ চলছে — পূর্ণ পর্যালোচনা শেষ না হওয়া পর্যন্ত এই পৃষ্ঠা ইনডেক্স বা পাবলিক ভাষা-নির্বাচনে সক্রিয় হবে না।",
        "verified":f"যাচাই করা হয়েছে: {REVIEW_DATE}","independent":"স্বাধীন তথ্য · সরকারি উৎস",
        "home":"হোম","routes":"পথসমূহ","daily":"দৈনন্দিন জীবন","contacts":"যোগাযোগ","faq":"সাধারণ প্রশ্ন","security":"প্রতারণা এড়ান",
        "practical":"ব্যবহারিক বিষয়","official":"সরকারি উৎস","check":"কোনো পদক্ষেপ নেওয়ার আগে সবসময় সরকারি উৎস যাচাই করুন।",
        "legal":"Guia Migrante PT একটি স্বাধীন পোর্টাল। কোনো অমিল হলে প্রযোজ্য আইন এবং সংশ্লিষ্ট কর্তৃপক্ষের সরকারি তথ্য অগ্রাধিকার পায়।",
        "source":"সরকারি উৎস ↗","menu":"মেনু খুলুন","skip":"মূল বিষয়বস্তুতে যান",
    },
}

DATA = {
"fr": {
"saude-completa.html":("Santé : centre de santé, SNS 24 et soins","Centre de santé, SNS 24, urgences et hôpital ont des fonctions différentes. L’objectif est d’accéder au niveau de soins adapté sans confondre inscription au SNS et gratuité automatique de tous les soins.",[
("Numéro d’usager SNS","Il identifie l’usager dans le système public, mais ne signifie pas à lui seul que tous les soins sont gratuits."),
("SNS 24 et urgences","Utilisez le canal approprié à la gravité de la situation et suivez les indications officielles."),
("Documents et couverture","Les règles peuvent dépendre de la résidence, de la situation et du type de soin. Vérifiez la règle applicable."),]),
"trabalho-direitos.html":("Travail et droits des travailleurs","Une personne étrangère qui travaille légalement au Portugal a, en matière de travail, les mêmes droits et devoirs fondamentaux qu’un travailleur portugais.",[
("Contrat et salaire","Conservez votre contrat, fiches de paie et preuves de paiement. Les conditions de travail doivent être claires."),
("Horaires, repos et congés","Le statut de migrant ne supprime pas les règles relatives aux horaires, repos, congés et sécurité au travail."),
("En cas de problème","Conservez les preuves et utilisez les canaux officiels compétents pour l’information ou la plainte."),]),
"habitacao.html":("Logement et location","La location est un domaine où l’urgence peut exposer les migrants aux arnaques. Contrat, identité du propriétaire, reçus, adresse et état du logement doivent être vérifiés avec soin.",[
("Avant de payer","Confirmez l’identité de la personne qui loue le bien et évitez les paiements sans preuve ou contrat clair."),
("Contrat et reçus","Conservez le contrat, les reçus et les échanges importants avec le propriétaire."),
("Adresse et conditions","Vérifiez ce qui est inclus dans le loyer, les charges et les conditions réelles du logement."),]),
"qualificacoes.html":("Reconnaissance des diplômes et qualifications","Une formation obtenue à l’étranger peut nécessiter une reconnaissance académique. Une profession réglementée peut aussi exiger une reconnaissance professionnelle par l’autorité compétente.",[
("Reconnaissance académique","Elle concerne le diplôme ou le niveau d’études et suit les règles de l’enseignement supérieur."),
("Profession réglementée","L’accès à certaines professions peut exiger une procédure supplémentaire auprès de l’autorité professionnelle compétente."),
("Ne confondez pas les deux","La reconnaissance d’un diplôme ne garantit pas automatiquement l’accès à une profession réglementée."),]),
"servicos-casa.html":("Électricité, eau, gaz et télécommunications","Énergie, eau et télécommunications ont des fournisseurs, contrats, factures et règles différentes. Vérifiez qui fournit chaque service et ce qui est inclus ou non dans le loyer.",[
("Contrats","Vérifiez le titulaire, la durée, la fidélisation éventuelle et les services inclus."),
("Factures","Lisez les montants, périodes, consommations et frais avant de payer."),
("Changement de fournisseur","Les règles varient selon le service. Utilisez les comparateurs et informations des régulateurs officiels lorsque disponibles."),]),
"apoios-sociais.html":("Prestations sociales et Sécurité sociale","Prestations familiales, chômage, maladie, parentalité et autres aides ont des conditions propres de résidence, cotisations, revenus, âge ou composition du foyer.",[
("Une aide n’est pas automatique","Le fait de résider au Portugal ne signifie pas que toutes les prestations sont accessibles."),
("Cotisations et revenus","Certaines prestations dépendent de la carrière contributive, des revenus ou de la composition familiale."),
("Vérifiez la prestation exacte","Consultez la Sécurité sociale pour les conditions et documents à jour."),]),
"banco-pagamentos.html":("Banque, compte et paiements","Les banques peuvent demander des pièces d’identité et des informations sur la résidence fiscale, la profession et l’origine des fonds. Les commissions et documents varient selon les établissements.",[
("Identification","Préparez des documents d’identité et les informations demandées sur votre résidence fiscale."),
("Frais","Comparez les commissions, cartes, virements et autres coûts avant d’ouvrir ou de changer de compte."),
("Sécurité","Ne partagez jamais codes, PIN ou mots de passe reçus pour l’authentification."),]),
"carta-conducao.html":("Permis de conduire étranger au Portugal","Les règles d’utilisation ou d’échange d’un permis étranger dépendent du pays émetteur, du type de permis et de la situation de résidence. Vérifiez toujours les règles de l’IMT.",[
("Pays émetteur","Les règles ne sont pas identiques pour tous les permis étrangers."),
("Résidence au Portugal","Le moment où vous établissez votre résidence peut modifier les obligations applicables."),
("Échange et documents","Les délais et documents peuvent varier. Vérifiez l’IMT avant de conduire ou de demander un échange."),]),
"consumidor.html":("Droits des consommateurs et réclamations","Contrats, services, achats et factures peuvent donner lieu à des droits de consommateur. Conservez les preuves et utilisez les mécanismes officiels de réclamation lorsque nécessaire.",[
("Conservez les preuves","Factures, contrats, reçus, courriels et captures peuvent être importants en cas de litige."),
("Réclamation","Utilisez le Livro de Reclamações ou l’autorité compétente lorsque le problème relève de ces mécanismes."),
("Avant de payer","Vérifiez l’identité du fournisseur, les conditions et les coûts annoncés."),]),
},
"es": {
"saude-completa.html":("Salud: centro de salud, SNS 24 y atención","Centro de salud, SNS 24, urgencias y hospital tienen funciones distintas. El objetivo es llegar al nivel de atención adecuado sin confundir inscripción en el SNS con gratuidad automática de todos los cuidados.",[("Número de usuario del SNS","Identifica al usuario en el sistema público, pero por sí solo no significa que toda la atención sea gratuita."),("SNS 24 y urgencias","Usa el canal adecuado según la gravedad y sigue las indicaciones oficiales."),("Documentos y cobertura","Las reglas pueden depender de residencia, situación y tipo de atención. Comprueba la regla aplicable.")]),
"trabalho-direitos.html":("Trabajo y derechos laborales","Una persona extranjera que trabaja legalmente en Portugal tiene, en materia laboral, los mismos derechos y deberes fundamentales que un trabajador portugués.",[("Contrato y salario","Guarda contrato, nóminas y comprobantes de pago. Las condiciones de trabajo deben estar claras."),("Horario, descanso y vacaciones","Ser migrante no elimina las reglas sobre horario, descanso, vacaciones y seguridad laboral."),("Si hay un problema","Conserva pruebas y utiliza los canales oficiales competentes para información o reclamación.")]),
"habitacao.html":("Vivienda y alquiler","El alquiler es un área donde la urgencia puede exponer a migrantes a estafas. Contrato, identidad del propietario, recibos, dirección y condiciones del inmueble deben verificarse con cuidado.",[("Antes de pagar","Comprueba quién alquila el inmueble y evita pagos sin prueba o contrato claro."),("Contrato y recibos","Guarda contrato, recibos y comunicaciones importantes con el propietario."),("Dirección y condiciones","Comprueba qué incluye el alquiler, gastos y condiciones reales de la vivienda.")]),
"qualificacoes.html":("Reconocimiento de títulos y cualificaciones","Una formación obtenida en el extranjero puede necesitar reconocimiento académico. Una profesión regulada puede además exigir reconocimiento profesional por la autoridad competente.",[("Reconocimiento académico","Se refiere al título o nivel de estudios y sigue las reglas de educación superior."),("Profesión regulada","El acceso a determinadas profesiones puede requerir un trámite adicional ante la autoridad profesional competente."),("No son lo mismo","Reconocer un título no garantiza automáticamente acceso a una profesión regulada.")]),
"servicos-casa.html":("Electricidad, agua, gas y telecomunicaciones","Energía, agua y telecomunicaciones tienen proveedores, contratos, facturas y reglas diferentes. Comprueba quién presta cada servicio y qué está incluido en el alquiler.",[("Contratos","Comprueba titular, duración, permanencia y servicios incluidos."),("Facturas","Revisa importes, periodos, consumos y cargos antes de pagar."),("Cambio de proveedor","Las reglas varían según el servicio. Utiliza comparadores e información oficial cuando existan.")]),
"apoios-sociais.html":("Ayudas sociales y Seguridad Social","Prestaciones familiares, desempleo, enfermedad, parentalidad y otras ayudas tienen requisitos propios de residencia, cotizaciones, ingresos, edad o composición del hogar.",[("No son automáticas","Residir en Portugal no significa tener derecho a todas las prestaciones."),("Cotizaciones e ingresos","Algunas prestaciones dependen de cotizaciones, ingresos o composición familiar."),("Comprueba la prestación exacta","Consulta la Seguridad Social para requisitos y documentos actualizados.")]),
"banco-pagamentos.html":("Banco, cuenta y pagos","Los bancos pueden pedir identificación e información sobre residencia fiscal, profesión y origen de fondos. Las comisiones y documentos varían entre entidades.",[("Identificación","Prepara documentos de identidad y la información solicitada sobre residencia fiscal."),("Costes","Compara comisiones, tarjetas, transferencias y otros costes antes de abrir o cambiar de cuenta."),("Seguridad","Nunca compartas códigos, PIN o contraseñas de autenticación.")]),
"carta-conducao.html":("Permiso de conducir extranjero en Portugal","Las reglas para usar o canjear un permiso extranjero dependen del país emisor, tipo de permiso y situación de residencia. Comprueba siempre las reglas del IMT.",[("País emisor","Las reglas no son iguales para todos los permisos extranjeros."),("Residencia en Portugal","El momento en que estableces residencia puede cambiar las obligaciones."),("Canje y documentos","Plazos y documentos pueden variar. Comprueba el IMT antes de conducir o pedir el canje.")]),
"consumidor.html":("Derechos del consumidor y reclamaciones","Contratos, servicios, compras y facturas pueden generar derechos de consumidor. Conserva pruebas y utiliza los mecanismos oficiales de reclamación cuando corresponda.",[("Guarda pruebas","Facturas, contratos, recibos, correos y capturas pueden ser importantes en un conflicto."),("Reclamación","Usa el Livro de Reclamações o la autoridad competente cuando sea aplicable."),("Antes de pagar","Comprueba identidad del proveedor, condiciones y costes anunciados.")]),
},
"uk": {
"saude-completa.html":("Охорона здоров’я: медичний центр, SNS 24 та допомога","Медичний центр, SNS 24, невідкладна допомога та лікарня мають різні функції. Реєстрація в SNS не означає автоматично безкоштовність усіх послуг.",[("Номер користувача SNS","Він ідентифікує вас у державній системі, але сам по собі не гарантує безкоштовність усіх послуг."),("SNS 24 і невідкладна допомога","Оберіть канал відповідно до серйозності ситуації та дотримуйтесь офіційних вказівок."),("Документи та покриття","Правила можуть залежати від проживання, статусу та виду допомоги.")]),
"trabalho-direitos.html":("Робота і трудові права","Іноземець, який законно працює в Португалії, має основні трудові права й обов’язки на тих самих засадах, що й португальський працівник.",[("Договір і зарплата","Зберігайте договір, розрахункові листи та докази виплат."),("Графік, відпочинок і відпустка","Міграційний статус не скасовує правил щодо робочого часу, відпочинку, відпусток і безпеки."),("Якщо виникла проблема","Зберігайте докази та звертайтеся через компетентні офіційні канали.")]),
"habitacao.html":("Житло та оренда","Терміновість пошуку житла може підвищувати ризик шахрайства. Перевіряйте договір, особу орендодавця, квитанції, адресу та реальний стан житла.",[("До оплати","Перевірте, хто здає житло, і не платіть без доказів або зрозумілого договору."),("Договір і квитанції","Зберігайте договір, квитанції та важливе листування."),("Умови","Перевірте, що входить в орендну плату та які додаткові витрати існують.")]),
"qualificacoes.html":("Визнання дипломів і кваліфікацій","Освіта, здобута за кордоном, може потребувати академічного визнання. Для регульованої професії може також знадобитися професійне визнання компетентним органом.",[("Академічне визнання","Стосується диплома або рівня освіти."),("Регульована професія","Для деяких професій потрібна окрема процедура у професійного органу."),("Не плутайте","Визнання диплома не завжди автоматично дає право працювати в регульованій професії.")]),
"servicos-casa.html":("Електроенергія, вода, газ і телекомунікації","Енергія, вода й телекомунікації мають різних постачальників, договори, рахунки та правила. Перевіряйте, що входить до орендної плати.",[("Договори","Перевіряйте власника договору, строк, можливу прив’язку та включені послуги."),("Рахунки","Перевіряйте суми, періоди, споживання та збори перед оплатою."),("Зміна постачальника","Правила відрізняються за послугою; використовуйте офіційні порівняльні інструменти та інформацію регуляторів.")]),
"apoios-sociais.html":("Соціальна підтримка і Segurança Social","Сімейні виплати, безробіття, хвороба, батьківство та інші види допомоги мають власні вимоги щодо проживання, внесків, доходу, віку чи складу сім’ї.",[("Не автоматично","Проживання в Португалії не означає автоматичного права на всі виплати."),("Внески та доходи","Деякі виплати залежать від страхового стажу, доходу або складу сім’ї."),("Перевірте конкретну виплату","Звертайтеся до Segurança Social за актуальними вимогами.")]),
"banco-pagamentos.html":("Банк, рахунок і платежі","Банки можуть вимагати посвідчення особи та дані про податкове резидентство, професію і походження коштів. Комісії та документи відрізняються.",[("Ідентифікація","Підготуйте посвідчення особи та дані про податкове резидентство."),("Витрати","Порівнюйте комісії, картки, перекази та інші витрати."),("Безпека","Ніколи не передавайте PIN, паролі або коди автентифікації.")]),
"carta-conducao.html":("Іноземне водійське посвідчення в Португалії","Правила використання або обміну іноземного посвідчення залежать від країни видачі, типу документа та статусу проживання. Завжди перевіряйте IMT.",[("Країна видачі","Правила відрізняються залежно від країни."),("Проживання","Дата встановлення проживання може впливати на обов’язки."),("Обмін і документи","Строки та документи відрізняються. Перевірте IMT до поїздок або подання заяви.")]),
"consumidor.html":("Права споживачів і скарги","Договори, послуги, покупки та рахунки можуть створювати права споживача. Зберігайте докази та використовуйте офіційні механізми скарг.",[("Зберігайте докази","Рахунки, договори, квитанції, листування й скриншоти можуть бути важливими."),("Скарга","За потреби використовуйте Livro de Reclamações або компетентний орган."),("До оплати","Перевіряйте постачальника, умови та заявлені витрати.")]),
},
"ru": {
"saude-completa.html":("Здравоохранение: медицинский центр, SNS 24 и помощь","Медицинский центр, SNS 24, неотложная помощь и больница выполняют разные функции. Регистрация в SNS не означает автоматически бесплатность всех услуг.",[("Номер пользователя SNS","Он идентифицирует вас в государственной системе, но сам по себе не гарантирует бесплатность всех услуг."),("SNS 24 и неотложная помощь","Выбирайте канал в зависимости от серьёзности ситуации и следуйте официальным указаниям."),("Документы и покрытие","Правила могут зависеть от проживания, статуса и вида медицинской помощи.")]),
"trabalho-direitos.html":("Работа и трудовые права","Иностранец, который законно работает в Португалии, имеет основные трудовые права и обязанности на тех же принципах, что и португальский работник.",[("Договор и зарплата","Храните договор, расчётные листы и подтверждения выплат."),("График, отдых и отпуск","Миграционный статус не отменяет правила о рабочем времени, отдыхе, отпуске и безопасности."),("Если возникла проблема","Сохраняйте доказательства и используйте официальные компетентные каналы.")]),
"habitacao.html":("Жильё и аренда","Срочность поиска жилья может повышать риск мошенничества. Проверяйте договор, личность арендодателя, квитанции, адрес и реальное состояние жилья.",[("До оплаты","Проверьте, кто сдаёт жильё, и не платите без подтверждения или понятного договора."),("Договор и квитанции","Храните договор, квитанции и важную переписку."),("Условия","Проверьте, что входит в аренду и какие дополнительные расходы существуют.")]),
"qualificacoes.html":("Признание дипломов и квалификаций","Образование, полученное за рубежом, может требовать академического признания. Для регулируемой профессии может дополнительно потребоваться профессиональное признание.",[("Академическое признание","Относится к диплому или уровню образования."),("Регулируемая профессия","Для некоторых профессий нужна отдельная процедура у компетентного профессионального органа."),("Не путайте","Признание диплома не всегда автоматически даёт право работать в регулируемой профессии.")]),
"servicos-casa.html":("Электричество, вода, газ и телекоммуникации","Энергия, вода и телекоммуникации имеют разных поставщиков, договоры, счета и правила. Проверяйте, что включено в аренду.",[("Договоры","Проверяйте владельца договора, срок, возможную привязку и включённые услуги."),("Счета","Проверяйте суммы, периоды, потребление и сборы перед оплатой."),("Смена поставщика","Правила зависят от услуги; используйте официальные сравнительные инструменты и информацию регуляторов.")]),
"apoios-sociais.html":("Социальная поддержка и Segurança Social","Семейные выплаты, безработица, болезнь, родительство и другие виды помощи имеют свои требования по проживанию, взносам, доходу, возрасту или составу семьи.",[("Не автоматически","Проживание в Португалии не означает автоматического права на все выплаты."),("Взносы и доходы","Некоторые выплаты зависят от страхового стажа, дохода или состава семьи."),("Проверьте конкретную выплату","Уточняйте актуальные требования в Segurança Social.")]),
"banco-pagamentos.html":("Банк, счёт и платежи","Банки могут запрашивать документы и сведения о налоговом резидентстве, профессии и происхождении средств. Комиссии и документы различаются.",[("Идентификация","Подготовьте документы и сведения о налоговом резидентстве."),("Расходы","Сравнивайте комиссии, карты, переводы и другие расходы."),("Безопасность","Никогда не передавайте PIN, пароли или коды аутентификации.")]),
"carta-conducao.html":("Иностранные водительские права в Португалии","Правила использования или обмена иностранных прав зависят от страны выдачи, типа документа и статуса проживания. Всегда проверяйте IMT.",[("Страна выдачи","Правила различаются в зависимости от страны."),("Проживание","Дата установления проживания может влиять на обязанности."),("Обмен и документы","Сроки и документы различаются. Проверьте IMT до вождения или подачи заявления.")]),
"consumidor.html":("Права потребителей и жалобы","Договоры, услуги, покупки и счета могут создавать права потребителя. Храните доказательства и используйте официальные механизмы жалоб.",[("Храните доказательства","Счета, договоры, квитанции, письма и скриншоты могут быть важны."),("Жалоба","При необходимости используйте Livro de Reclamações или компетентный орган."),("До оплаты","Проверяйте поставщика, условия и заявленные расходы.")]),
},
"hi": {
"saude-completa.html":("स्वास्थ्य: स्वास्थ्य केंद्र, SNS 24 और देखभाल","स्वास्थ्य केंद्र, SNS 24, आपातकालीन सेवा और अस्पताल की भूमिकाएँ अलग हैं। SNS में पंजीकरण का अर्थ यह नहीं कि हर उपचार स्वतः मुफ्त होगा।",[("SNS उपयोगकर्ता संख्या","यह सार्वजनिक स्वास्थ्य प्रणाली में आपकी पहचान करती है, लेकिन सभी सेवाओं की मुफ्त उपलब्धता की गारंटी नहीं देती।"),("SNS 24 और आपातकाल","स्थिति की गंभीरता के अनुसार सही चैनल चुनें और आधिकारिक निर्देशों का पालन करें।"),("दस्तावेज़ और कवरेज","नियम निवास, स्थिति और देखभाल के प्रकार पर निर्भर हो सकते हैं।")]),
"trabalho-direitos.html":("काम और श्रम अधिकार","पुर्तगाल में कानूनी रूप से काम करने वाला विदेशी कर्मचारी मूल श्रम अधिकारों और दायित्वों में पुर्तगाली कर्मचारी के समान सुरक्षा रखता है।",[("अनुबंध और वेतन","अनुबंध, वेतन पर्ची और भुगतान के प्रमाण सुरक्षित रखें।"),("काम के घंटे, आराम और छुट्टी","प्रवासी होना काम के घंटे, आराम, छुट्टी या सुरक्षा के नियम समाप्त नहीं करता।"),("समस्या होने पर","प्रमाण सुरक्षित रखें और सक्षम आधिकारिक चैनल का उपयोग करें।")]),
"habitacao.html":("आवास और किराया","जल्दी घर खोजने की जरूरत प्रवासियों को धोखाधड़ी के जोखिम में डाल सकती है। अनुबंध, मकान मालिक की पहचान, रसीदें, पता और घर की वास्तविक स्थिति जाँचें।",[("भुगतान से पहले","किराये पर देने वाले व्यक्ति की पहचान जाँचें और बिना प्रमाण या स्पष्ट अनुबंध भुगतान न करें।"),("अनुबंध और रसीदें","अनुबंध, रसीदें और महत्वपूर्ण संदेश सुरक्षित रखें।"),("शर्तें","किराये में क्या शामिल है और कौन-से अतिरिक्त खर्च हैं, यह जाँचें।")]),
"qualificacoes.html":("डिग्री और योग्यता की मान्यता","विदेश में प्राप्त शिक्षा के लिए अकादमिक मान्यता की जरूरत हो सकती है। विनियमित पेशे के लिए संबंधित प्राधिकरण से पेशेवर मान्यता भी आवश्यक हो सकती है।",[("अकादमिक मान्यता","यह डिग्री या शिक्षा स्तर से संबंधित होती है।"),("विनियमित पेशा","कुछ पेशों में सक्षम पेशेवर निकाय की अलग प्रक्रिया आवश्यक होती है।"),("दोनों अलग हैं","डिग्री की मान्यता से विनियमित पेशे में काम करने का अधिकार स्वतः नहीं मिलता।")]),
"servicos-casa.html":("बिजली, पानी, गैस और दूरसंचार","ऊर्जा, पानी और दूरसंचार के प्रदाता, अनुबंध, बिल और नियम अलग-अलग होते हैं। जाँचें कि किराये में कौन-सी सेवाएँ शामिल हैं।",[("अनुबंध","खाता धारक, अवधि, लॉक-इन और शामिल सेवाएँ जाँचें।"),("बिल","भुगतान से पहले राशि, अवधि, उपयोग और शुल्क जाँचें।"),("प्रदाता बदलना","नियम सेवा के अनुसार बदलते हैं; उपलब्ध आधिकारिक तुलना उपकरणों का उपयोग करें।")]),
"apoios-sociais.html":("सामाजिक सहायता और Segurança Social","परिवार, बेरोज़गारी, बीमारी, मातृत्व/पितृत्व और अन्य सहायता के लिए निवास, योगदान, आय, उम्र या परिवार संरचना की अलग शर्तें हो सकती हैं।",[("स्वतः अधिकार नहीं","पुर्तगाल में रहना सभी लाभों का स्वतः अधिकार नहीं देता।"),("योगदान और आय","कुछ लाभ योगदान रिकॉर्ड, आय या परिवार संरचना पर निर्भर करते हैं।"),("सही लाभ जाँचें","ताज़ा शर्तों के लिए Segurança Social की आधिकारिक जानकारी देखें।")]),
"banco-pagamentos.html":("बैंक, खाता और भुगतान","बैंक पहचान, कर निवास, पेशा और धन के स्रोत की जानकारी मांग सकते हैं। शुल्क और दस्तावेज़ बैंक के अनुसार बदलते हैं।",[("पहचान","पहचान दस्तावेज़ और कर निवास की जानकारी तैयार रखें।"),("शुल्क","खाता खोलने या बदलने से पहले शुल्क, कार्ड और ट्रांसफर लागत की तुलना करें।"),("सुरक्षा","PIN, पासवर्ड या प्रमाणीकरण कोड किसी से साझा न करें।")]),
"carta-conducao.html":("पुर्तगाल में विदेशी ड्राइविंग लाइसेंस","विदेशी लाइसेंस के उपयोग या विनिमय के नियम जारी करने वाले देश, लाइसेंस के प्रकार और निवास स्थिति पर निर्भर करते हैं। हमेशा IMT की जानकारी जाँचें।",[("जारी करने वाला देश","सभी विदेशी लाइसेंस पर एक जैसे नियम लागू नहीं होते।"),("पुर्तगाल में निवास","निवास स्थापित करने की तारीख दायित्व बदल सकती है।"),("विनिमय और दस्तावेज़","समय-सीमा और दस्तावेज़ बदल सकते हैं; ड्राइविंग या विनिमय से पहले IMT जाँचें।")]),
"consumidor.html":("उपभोक्ता अधिकार और शिकायतें","अनुबंध, सेवाएँ, खरीद और बिल उपभोक्ता अधिकार पैदा कर सकते हैं। प्रमाण सुरक्षित रखें और जरूरत पड़ने पर आधिकारिक शिकायत प्रणाली का उपयोग करें।",[("प्रमाण सुरक्षित रखें","बिल, अनुबंध, रसीद, ईमेल और स्क्रीनशॉट विवाद में महत्वपूर्ण हो सकते हैं।"),("शिकायत","लागू होने पर Livro de Reclamações या सक्षम प्राधिकरण का उपयोग करें।"),("भुगतान से पहले","प्रदाता की पहचान, शर्तें और घोषित लागत जाँचें।")]),
},
"bn": {
"saude-completa.html":("স্বাস্থ্য: স্বাস্থ্যকেন্দ্র, SNS 24 ও চিকিৎসা","স্বাস্থ্যকেন্দ্র, SNS 24, জরুরি বিভাগ ও হাসপাতালের কাজ আলাদা। SNS-এ নিবন্ধন মানেই সব চিকিৎসা স্বয়ংক্রিয়ভাবে বিনামূল্যে নয়।",[("SNS ব্যবহারকারী নম্বর","এটি সরকারি স্বাস্থ্যব্যবস্থায় পরিচয় নিশ্চিত করে, তবে সব সেবা বিনামূল্যে হবে এমন নিশ্চয়তা দেয় না।"),("SNS 24 ও জরুরি সেবা","পরিস্থিতির গুরুত্ব অনুযায়ী সঠিক চ্যানেল ব্যবহার করুন এবং সরকারি নির্দেশনা অনুসরণ করুন।"),("নথি ও কভারেজ","নিয়ম বাসস্থান, অবস্থা ও চিকিৎসার ধরনের ওপর নির্ভর করতে পারে।")]),
"trabalho-direitos.html":("কাজ ও শ্রম অধিকার","পর্তুগালে বৈধভাবে কাজ করা বিদেশি কর্মীর মৌলিক শ্রম অধিকার ও দায়িত্ব পর্তুগিজ কর্মীর মতোই সুরক্ষিত।",[("চুক্তি ও বেতন","চুক্তি, বেতন স্লিপ ও পেমেন্টের প্রমাণ সংরক্ষণ করুন।"),("কাজের সময়, বিশ্রাম ও ছুটি","অভিবাসী হওয়া কাজের সময়, বিশ্রাম, ছুটি বা নিরাপত্তার নিয়ম বাতিল করে না।"),("সমস্যা হলে","প্রমাণ সংরক্ষণ করুন এবং সংশ্লিষ্ট সরকারি চ্যানেল ব্যবহার করুন।")]),
"habitacao.html":("বাসস্থান ও ভাড়া","দ্রুত বাসা খোঁজার প্রয়োজন অভিবাসীদের প্রতারণার ঝুঁকিতে ফেলতে পারে। চুক্তি, বাড়িওয়ালার পরিচয়, রসিদ, ঠিকানা ও বাসার বাস্তব অবস্থা যাচাই করুন।",[("পেমেন্টের আগে","কে বাসা ভাড়া দিচ্ছেন তা যাচাই করুন এবং স্পষ্ট চুক্তি বা প্রমাণ ছাড়া টাকা দেবেন না।"),("চুক্তি ও রসিদ","চুক্তি, রসিদ ও গুরুত্বপূর্ণ যোগাযোগ সংরক্ষণ করুন।"),("শর্ত","ভাড়ার মধ্যে কী অন্তর্ভুক্ত এবং অতিরিক্ত খরচ কী আছে তা যাচাই করুন।")]),
"qualificacoes.html":("ডিগ্রি ও যোগ্যতার স্বীকৃতি","বিদেশে অর্জিত শিক্ষার জন্য একাডেমিক স্বীকৃতি লাগতে পারে। নিয়ন্ত্রিত পেশায় সংশ্লিষ্ট কর্তৃপক্ষের পেশাগত স্বীকৃতিও প্রয়োজন হতে পারে।",[("একাডেমিক স্বীকৃতি","এটি ডিগ্রি বা শিক্ষার স্তর নিয়ে কাজ করে।"),("নিয়ন্ত্রিত পেশা","কিছু পেশায় সংশ্লিষ্ট পেশাগত সংস্থার আলাদা প্রক্রিয়া লাগে।"),("এক নয়","ডিগ্রির স্বীকৃতি পেলেই নিয়ন্ত্রিত পেশায় কাজের অধিকার স্বয়ংক্রিয়ভাবে পাওয়া যায় না।")]),
"servicos-casa.html":("বিদ্যুৎ, পানি, গ্যাস ও টেলিযোগাযোগ","জ্বালানি, পানি ও টেলিযোগাযোগে আলাদা সরবরাহকারী, চুক্তি, বিল ও নিয়ম থাকে। ভাড়ার মধ্যে কোন সেবা অন্তর্ভুক্ত তা যাচাই করুন।",[("চুক্তি","চুক্তির নাম, সময়কাল, লক-ইন ও অন্তর্ভুক্ত সেবা যাচাই করুন।"),("বিল","পেমেন্টের আগে পরিমাণ, সময়কাল, ব্যবহার ও ফি যাচাই করুন।"),("সরবরাহকারী বদল","নিয়ম সেবাভেদে বদলে যায়; সরকারি তুলনা ও নিয়ন্ত্রক তথ্য ব্যবহার করুন।")]),
"apoios-sociais.html":("সামাজিক সহায়তা ও Segurança Social","পরিবার, বেকারত্ব, অসুস্থতা, মাতৃত্ব/পিতৃত্ব ও অন্যান্য সহায়তার জন্য বাসস্থান, অবদান, আয়, বয়স বা পরিবারের গঠনভিত্তিক আলাদা শর্ত থাকতে পারে।",[("স্বয়ংক্রিয় অধিকার নয়","পর্তুগালে থাকা মানেই সব সুবিধা পাওয়ার অধিকার নয়।"),("অবদান ও আয়","কিছু সুবিধা অবদানের ইতিহাস, আয় বা পরিবারের গঠনের ওপর নির্ভর করে।"),("সঠিক সুবিধা যাচাই করুন","হালনাগাদ শর্তের জন্য Segurança Social-এর সরকারি তথ্য দেখুন।")]),
"banco-pagamentos.html":("ব্যাংক, অ্যাকাউন্ট ও পেমেন্ট","ব্যাংক পরিচয়, কর-বাসস্থান, পেশা ও অর্থের উৎস সম্পর্কে তথ্য চাইতে পারে। ফি ও নথি ব্যাংকভেদে বদলে যায়।",[("পরিচয়","পরিচয়পত্র ও কর-বাসস্থানের তথ্য প্রস্তুত রাখুন।"),("খরচ","অ্যাকাউন্ট খোলা বা বদলের আগে ফি, কার্ড ও ট্রান্সফার খরচ তুলনা করুন।"),("নিরাপত্তা","PIN, পাসওয়ার্ড বা অথেনটিকেশন কোড কখনো শেয়ার করবেন না।")]),
"carta-conducao.html":("পর্তুগালে বিদেশি ড্রাইভিং লাইসেন্স","বিদেশি লাইসেন্স ব্যবহার বা বিনিময়ের নিয়ম ইস্যুকারী দেশ, লাইসেন্সের ধরন ও বাসস্থান অবস্থার ওপর নির্ভর করে। সবসময় IMT যাচাই করুন।",[("ইস্যুকারী দেশ","সব বিদেশি লাইসেন্সের জন্য একই নিয়ম নয়।"),("পর্তুগালে বাসস্থান","বাসস্থান স্থাপনের তারিখ প্রযোজ্য দায়িত্ব বদলাতে পারে।"),("বিনিময় ও নথি","সময়সীমা ও নথি বদলাতে পারে; গাড়ি চালানো বা বিনিময়ের আগে IMT যাচাই করুন।")]),
"consumidor.html":("ভোক্তা অধিকার ও অভিযোগ","চুক্তি, সেবা, কেনাকাটা ও বিল থেকে ভোক্তা অধিকার তৈরি হতে পারে। প্রমাণ সংরক্ষণ করুন এবং প্রয়োজনে সরকারি অভিযোগ ব্যবস্থার ব্যবহার করুন।",[("প্রমাণ রাখুন","বিল, চুক্তি, রসিদ, ইমেইল ও স্ক্রিনশট বিরোধে গুরুত্বপূর্ণ হতে পারে।"),("অভিযোগ","প্রযোজ্য হলে Livro de Reclamações বা সংশ্লিষ্ট কর্তৃপক্ষ ব্যবহার করুন।"),("পেমেন্টের আগে","সরবরাহকারীর পরিচয়, শর্ত ও ঘোষিত খরচ যাচাই করুন।")]),
},
}

OFFICIAL = [
    ("gov.pt", "https://www.gov.pt/"),
    ("Segurança Social", "https://www.seg-social.pt/"),
    ("SNS 24", "https://www.sns24.gov.pt/"),
    ("IMT", "https://www.imt-ip.pt/"),
    ("Banco de Portugal", "https://clientebancario.bportugal.pt/"),
    ("Livro de Reclamações", "https://www.livroreclamacoes.pt/"),
]


def source_ids(page: str) -> str:
    if not SOURCE_CFG.exists():
        return ""
    try:
        data = json.loads(SOURCE_CFG.read_text(encoding="utf-8"))
    except Exception:
        return ""
    ids=[]
    for src in data.get("sources",[]):
        pages=set(src.get("pages",[]))
        if page in pages or f"en/{page}" in pages:
            if src.get("id"): ids.append(src["id"])
    return " ".join(sorted(set(ids)))


def render(locale: str, page: str, entry) -> str:
    title, lead, cards = entry
    u=UI[locale]
    nav=[("index.html",u["home"]),("percursos.html",u["routes"]),("dia-a-dia.html",u["daily"]),("contactos.html",u["contacts"]),("faq.html",u["faq"]),("seguranca.html",u["security"])]
    nav_html=''.join(f'<a href="{p}">{html.escape(label)}</a>' for p,label in nav)
    card_html=''.join(f'<article class="card"><h3>{html.escape(h)}</h3><p>{html.escape(t)}</p></article>' for h,t in cards)
    official_html=''.join(f'<a class="card" href="{url}" target="_blank" rel="noopener"><h3>{html.escape(name)}</h3><p>{html.escape(u["source"])}</p></a>' for name,url in OFFICIAL)
    ids=source_ids(page)
    meta=f'<meta name="official-source-ids" content="{html.escape(ids)}">' if ids else ''
    return f'''<!doctype html>
<html lang="{locale}"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#09315c">
<meta name="description" content="{html.escape(lead, quote=True)}"><meta name="last-reviewed" content="{REVIEW_ISO}"><meta name="robots" content="noindex,nofollow">{meta}
<title>{html.escape(title)} | Guia Migrante PT</title><link rel="canonical" href="{BASE}/{locale}/{page}"><link rel="alternate" hreflang="pt-PT" href="{BASE}/{page}"><link rel="alternate" hreflang="en" href="{BASE}/en/{page}">
<link rel="icon" href="../favicon.png"><link rel="stylesheet" href="../locale-core.css"><link rel="stylesheet" href="../language-switcher.css">
</head><body>
<a class="skip-link" href="#content">{html.escape(u['skip'])}</a>
<div class="topbar"><div class="container">{html.escape(u['independent'])} · {html.escape(u['verified'])}</div></div>
<header><div class="container header-inner"><a class="brand" href="index.html"><img src="../logo-guia-migrante-256.png" alt=""><span><strong>Guia Migrante PT</strong></span></a><nav class="desktop-nav">{nav_html}</nav><div class="header-actions"><div class="site-lang"><a href="../{page}">PT</a><a href="../en/{page}">EN</a><a class="active" href="{page}">{locale.upper()}</a></div><button class="menu-btn" id="menuButton" type="button" aria-expanded="false" aria-controls="mobileNav" aria-label="{html.escape(u['menu'])}">☰</button></div></div><nav class="mobile-nav" id="mobileNav">{nav_html}</nav></header><div class="brand-stripe"></div>
<div class="review-strip"><div class="container"><span class="review-badge">{html.escape(u['name'])}</span><span>{html.escape(u['stage'])}</span></div></div>
<main id="content"><section class="hero"><div class="container"><span class="kicker">{html.escape(u['daily'])}</span><h1>{html.escape(title)}</h1><p>{html.escape(lead)}</p><div class="hero-actions"><a class="btn primary" href="dia-a-dia.html">{html.escape(u['daily'])}</a><a class="btn secondary" href="contactos.html">{html.escape(u['contacts'])}</a></div></div></section>
<section class="content"><div class="container"><div class="section-head"><h2>{html.escape(u['practical'])}</h2><p>{html.escape(u['check'])}</p></div><div class="grid three">{card_html}</div></div></section>
<section class="content white"><div class="container"><div class="section-head"><h2>{html.escape(u['official'])}</h2><p>{html.escape(u['verified'])}. {html.escape(u['check'])}</p></div><div class="grid three">{official_html}</div></div></section></main>
<footer><div class="container footer-bottom"><span>© 2026 Guia Migrante PT</span><span>{html.escape(u['legal'])}</span></div></footer>
<script>const mb=document.getElementById('menuButton'),mn=document.getElementById('mobileNav');if(mb&&mn)mb.addEventListener('click',()=>{{const o=mn.classList.toggle('open');mb.setAttribute('aria-expanded',String(o));}});</script><script src="../language-switcher.js" defer></script>
</body></html>'''


def build() -> None:
    total=0
    for locale, pages in DATA.items():
        target=SITE/locale
        target.mkdir(parents=True, exist_ok=True)
        for page in PAGES:
            if page not in pages:
                raise SystemExit(f"missing {locale}/{page}")
            (target/page).write_text(render(locale,page,pages[page]),encoding="utf-8")
            total+=1
    print(f"Built staged living-in-Portugal translations: {total} pages across {len(DATA)} locales")

if __name__ == "__main__":
    build()
