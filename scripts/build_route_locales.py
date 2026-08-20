#!/usr/bin/env python3
from __future__ import annotations

import html, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'
SOURCE_CFG=ROOT/'monitor'/'sources.json'
BASE='https://guia-migrante-pt.pages.dev'
REVIEW_ISO='2026-08-20'
REVIEW_DATE='20/08/2026'

ROUTES=[
 'fora-de-portugal.html','ue-familiares.html','pais-terceiro.html','cplp.html','trabalho.html',
 'independente-empreendedor.html','nomada-digital.html','altamente-qualificado.html','estudantes.html',
 'rendimentos-proprios.html','familia.html','investimento.html','asilo.html','protecao-temporaria.html',
 'longa-duracao.html','situacoes-especiais.html','integracao.html'
]

COMMON={
'fr':{'name':'Français','ind':'Information indépendante · Vérifiée à partir de sources officielles','checked':f'Verifié le {REVIEW_DATE}','brand':'Information · Orientation · Confiance','stage':'Traduction en cours — cette version reste hors index jusqu’à la relecture complète.','routes':'Parcours','contacts':'Contacts','source':'Source officielle ↗','official':'Sources officielles','section':'Avant d’agir','intro':'Confirmez toujours la voie applicable à votre situation réelle, les documents demandés et le canal officiel actuellement ouvert.','cards':[('Base juridique','Identifiez d’abord la base exacte de votre séjour ou de votre entrée au Portugal.'),('Documents','Les documents, délais et frais varient selon la voie et peuvent changer.'),('Vérification officielle','Ne payez ni n’envoyez de documents sensibles avant de confirmer les informations sur le site de l’autorité compétente.')], 'legal':'Guia Migrante PT est indépendant et ne représente aucune autorité publique.'},
'es':{'name':'Español','ind':'Información independiente · Verificada con fuentes oficiales','checked':f'Verificado el {REVIEW_DATE}','brand':'Información · Orientación · Confianza','stage':'Traducción en curso — esta versión permanece fuera del índice hasta completar la revisión.','routes':'Rutas','contacts':'Contactos','source':'Fuente oficial ↗','official':'Fuentes oficiales','section':'Antes de actuar','intro':'Confirma siempre la vía aplicable a tu situación real, los documentos exigidos y el canal oficial que esté abierto en ese momento.','cards':[('Base jurídica','Identifica primero la base exacta de tu estancia o entrada en Portugal.'),('Documentos','Los documentos, plazos y tasas varían según la vía y pueden cambiar.'),('Comprobación oficial','No pagues ni envíes documentos sensibles antes de confirmar la información en la web de la autoridad competente.')], 'legal':'Guia Migrante PT es independiente y no representa a ninguna autoridad pública.'},
'uk':{'name':'Українська','ind':'Незалежна інформація · Перевірено за офіційними джерелами','checked':f'Перевірено {REVIEW_DATE}','brand':'Інформація · Орієнтація · Довіра','stage':'Переклад триває — ця версія не індексується до завершення повної перевірки.','routes':'Маршрути','contacts':'Контакти','source':'Офіційне джерело ↗','official':'Офіційні джерела','section':'Перед діями','intro':'Завжди перевіряйте, який саме шлях застосовується до вашої ситуації, які документи потрібні та який офіційний канал зараз відкритий.','cards':[('Правова підстава','Спочатку визначте точну правову підставу для вашого перебування або в’їзду до Португалії.'),('Документи','Документи, строки та збори залежать від маршруту і можуть змінюватися.'),('Офіційна перевірка','Не сплачуйте кошти й не надсилайте чутливі документи, доки не перевірите інформацію на сайті компетентного органу.')], 'legal':'Guia Migrante PT є незалежним і не представляє жоден державний орган.'},
'ru':{'name':'Русский','ind':'Независимая информация · Проверено по официальным источникам','checked':f'Проверено {REVIEW_DATE}','brand':'Информация · Ориентация · Доверие','stage':'Перевод продолжается — эта версия не индексируется до завершения полной проверки.','routes':'Маршруты','contacts':'Контакты','source':'Официальный источник ↗','official':'Официальные источники','section':'Перед действиями','intro':'Всегда проверяйте, какой именно путь применяется к вашей ситуации, какие документы нужны и какой официальный канал сейчас открыт.','cards':[('Правовое основание','Сначала определите точное правовое основание вашего пребывания или въезда в Португалию.'),('Документы','Документы, сроки и сборы зависят от выбранного пути и могут меняться.'),('Официальная проверка','Не платите и не отправляйте чувствительные документы, пока не подтвердите информацию на сайте компетентного органа.')], 'legal':'Guia Migrante PT независим и не представляет ни один государственный орган.'},
'hi':{'name':'हिन्दी','ind':'स्वतंत्र जानकारी · आधिकारिक स्रोतों से सत्यापित','checked':f'सत्यापित: {REVIEW_DATE}','brand':'जानकारी · मार्गदर्शन · भरोसा','stage':'अनुवाद जारी है — पूरी समीक्षा होने तक यह संस्करण खोज इंजन में सूचीबद्ध नहीं किया जाएगा।','routes':'मार्ग','contacts':'संपर्क','source':'आधिकारिक स्रोत ↗','official':'आधिकारिक स्रोत','section':'कदम उठाने से पहले','intro':'हमेशा यह पुष्टि करें कि आपकी वास्तविक स्थिति पर कौन-सा मार्ग लागू होता है, कौन-से दस्तावेज़ चाहिए और कौन-सा आधिकारिक चैनल अभी खुला है।','cards':[('कानूनी आधार','सबसे पहले पुर्तगाल में आपके प्रवेश या निवास का सही कानूनी आधार पहचानें।'),('दस्तावेज़','दस्तावेज़, समय-सीमा और शुल्क मार्ग के अनुसार बदलते हैं और समय के साथ बदल सकते हैं।'),('आधिकारिक पुष्टि','पैसा देने या संवेदनशील दस्तावेज़ भेजने से पहले सक्षम प्राधिकरण की वेबसाइट पर जानकारी सत्यापित करें।')], 'legal':'Guia Migrante PT स्वतंत्र है और किसी सार्वजनिक प्राधिकरण का प्रतिनिधित्व नहीं करता।'},
'bn':{'name':'বাংলা','ind':'স্বাধীন তথ্য · সরকারি উৎসের ভিত্তিতে যাচাইকৃত','checked':f'যাচাই করা হয়েছে: {REVIEW_DATE}','brand':'তথ্য · দিকনির্দেশনা · আস্থা','stage':'অনুবাদ চলছে — পূর্ণ পর্যালোচনা শেষ না হওয়া পর্যন্ত এই সংস্করণ সার্চ ইঞ্জিনে সূচিবদ্ধ হবে না।','routes':'পথসমূহ','contacts':'যোগাযোগ','source':'সরকারি উৎস ↗','official':'সরকারি উৎস','section':'পদক্ষেপ নেওয়ার আগে','intro':'আপনার বাস্তব পরিস্থিতিতে কোন পথ প্রযোজ্য, কোন নথি দরকার এবং কোন সরকারি চ্যানেল বর্তমানে খোলা আছে তা সবসময় যাচাই করুন।','cards':[('আইনি ভিত্তি','প্রথমে পর্তুগালে আপনার প্রবেশ বা থাকার সঠিক আইনি ভিত্তি নির্ধারণ করুন।'),('নথি','নথি, সময়সীমা ও ফি পথভেদে আলাদা এবং পরিবর্তিত হতে পারে।'),('সরকারি যাচাই','অর্থ প্রদান বা সংবেদনশীল নথি পাঠানোর আগে সংশ্লিষ্ট কর্তৃপক্ষের ওয়েবসাইটে তথ্য যাচাই করুন।')], 'legal':'Guia Migrante PT স্বাধীন এবং কোনো সরকারি কর্তৃপক্ষের প্রতিনিধি নয়।'}
}

P={
'fr':{
'fora-de-portugal.html':('Je suis encore hors du Portugal','Avant de voyager, choisissez une voie d’entrée correspondant à votre objectif réel : travail, études, activité indépendante, revenus propres, travail à distance, activité hautement qualifiée ou autre base légale.'),
'ue-familiares.html':('Je suis citoyen de l’UE/EEE/Suisse ou membre de famille','Les citoyens de l’UE/EEE/Suisse et certains membres de leur famille suivent un régime de libre circulation différent de celui des ressortissants de pays tiers.'),
'pais-terceiro.html':('Je suis ressortissant d’un pays tiers','Cette catégorie couvre plusieurs voies distinctes : travail, études, famille, CPLP, revenus propres, travail à distance et autres.'),
'cplp.html':('Je suis ressortissant d’un pays CPLP','Le titre de séjour CPLP suit des règles propres de visa, de rendez-vous et de délivrance du titre.'),
'trabalho.html':('Je veux travailler au Portugal','Emploi salarié, recherche d’emploi, travail saisonnier, activité indépendante, télétravail et activité hautement qualifiée ne sont pas la même procédure.'),
'independente-empreendedor.html':('Je suis indépendant ou entrepreneur','L’activité indépendante peut reposer sur des services, une profession ou une entreprise. Pour les personnes à l’étranger, une voie de visa spécifique peut s’appliquer.'),
'nomada-digital.html':('Je travaille à distance pour l’étranger','Il existe une voie de séjour pour l’activité professionnelle exercée à distance pour des personnes ou entités établies hors du Portugal.'),
'altamente-qualificado.html':('Je suis un professionnel hautement qualifié','La voie générale, la Carte bleue européenne et le Tech Visa sont des régimes différents. Le profil, le contrat, l’employeur et les qualifications sont déterminants.'),
'estudantes.html':('Je vais étudier, faire de la recherche ou un stage','Enseignement supérieur, échange, stage, volontariat et recherche peuvent relever de règles différentes selon le programme et sa durée.'),
'rendimentos-proprios.html':('Je suis retraité ou je vis de mes propres revenus','Le Portugal prévoit une voie de visa de séjour pour les retraités, certaines personnes religieuses et les personnes disposant de revenus propres.'),
'familia.html':('Je veux rejoindre ou vivre avec ma famille','La voie familiale dépend de la nationalité de la personne de référence, de son droit de séjour et du fait que le membre de famille soit au Portugal ou à l’étranger.'),
'investimento.html':('Je suis investisseur / demandeur ARI','L’autorisation de séjour pour investissement est un régime spécifique et ne doit pas être confondue avec une voie ordinaire de travail ou d’entrepreneuriat.'),
'asilo.html':('Je veux demander l’asile / la protection internationale','L’asile n’est pas un visa de travail ni un titre de séjour ordinaire. Il suit une procédure propre de protection internationale.'),
'protecao-temporaria.html':('J’ai une protection temporaire / je suis déplacé d’Ukraine','Le régime de protection temporaire pour les personnes déplacées d’Ukraine a des règles spécifiques d’éligibilité, d’enregistrement, de documents et de transition.'),
'longa-duracao.html':('Je vis légalement au Portugal depuis plusieurs années','Le statut de résident de longue durée est un régime spécifique. Les citoyens de l’UE ont des documents de séjour permanent distincts.'),
'situacoes-especiais.html':('J’ai une situation spéciale ou vulnérable','Mineurs, victimes de traite, situations humanitaires et autres cas exceptionnels doivent être orientés selon leur régime propre.'),
'integracao.html':('Je vis déjà au Portugal et je veux organiser mon intégration','Après les documents migratoires, la vie pratique comprend le travail, la santé, les impôts, la Sécurité sociale, l’école, les qualifications, le portugais, le logement et l’aide locale.')},
'es':{
'fora-de-portugal.html':('Todavía estoy fuera de Portugal','Antes de viajar, elige una vía de entrada que corresponda a tu objetivo real: trabajo, estudios, actividad por cuenta propia, ingresos propios, trabajo remoto, actividad altamente cualificada u otra base legal.'),
'ue-familiares.html':('Soy ciudadano de la UE/EEE/Suiza o familiar','Los ciudadanos de la UE/EEE/Suiza y determinados familiares siguen un régimen de libre circulación distinto del aplicable a nacionales de terceros países.'),
'pais-terceiro.html':('Soy nacional de un tercer país','Esta categoría incluye varias vías distintas: trabajo, estudios, familia, CPLP, ingresos propios, trabajo remoto y otras.'),
'cplp.html':('Soy nacional de un país CPLP','El permiso CPLP tiene reglas propias sobre visado, cita y emisión del título de residencia.'),
'trabalho.html':('Quiero trabajar en Portugal','Trabajo por cuenta ajena, búsqueda de empleo, trabajo estacional, actividad independiente, teletrabajo y actividad altamente cualificada no son el mismo procedimiento.'),
'independente-empreendedor.html':('Soy autónomo o emprendedor','La actividad independiente puede basarse en servicios, una profesión o una empresa. Para quien aún está fuera de Portugal puede existir una vía específica de visado.'),
'nomada-digital.html':('Trabajo a distancia para el extranjero','Existe una vía de residencia para actividad profesional realizada a distancia para personas o entidades establecidas fuera de Portugal.'),
'altamente-qualificado.html':('Soy un profesional altamente cualificado','La vía general, la Tarjeta Azul UE y el Tech Visa son regímenes distintos. El perfil, contrato, empleador y cualificaciones son determinantes.'),
'estudantes.html':('Voy a estudiar, investigar o hacer prácticas','Educación superior, intercambio, prácticas, voluntariado e investigación pueden tener reglas diferentes según el programa y su duración.'),
'rendimentos-proprios.html':('Soy jubilado o vivo de mis propios ingresos','Portugal dispone de una vía de visado de residencia para jubilados, determinadas personas religiosas y personas que viven de ingresos propios.'),
'familia.html':('Quiero reunirme o vivir con mi familia','La vía familiar depende de la nacionalidad y el derecho de residencia de la persona de referencia y de si el familiar está dentro o fuera de Portugal.'),
'investimento.html':('Soy inversor / solicitante ARI','La autorización de residencia por inversión es un régimen específico y no debe confundirse con una vía ordinaria de trabajo o emprendimiento.'),
'asilo.html':('Quiero pedir asilo / protección internacional','El asilo no es un visado de trabajo ni una residencia ordinaria. Sigue un procedimiento propio de protección internacional.'),
'protecao-temporaria.html':('Tengo protección temporal / fui desplazado de Ucrania','La protección temporal para personas desplazadas de Ucrania tiene reglas específicas de elegibilidad, registro, documentos y transición.'),
'longa-duracao.html':('Vivo legalmente en Portugal desde hace varios años','El estatuto de residente de larga duración es un régimen específico. Los ciudadanos de la UE tienen documentos distintos de residencia permanente.'),
'situacoes-especiais.html':('Tengo una situación especial o vulnerable','Menores, víctimas de trata, situaciones humanitarias y otros casos excepcionales deben orientarse según su régimen específico.'),
'integracao.html':('Ya vivo en Portugal y quiero organizar mi integración','Después de los documentos migratorios, la vida práctica incluye trabajo, salud, impuestos, Seguridad Social, escuela, cualificaciones, portugués, vivienda y apoyo local.')},
'uk':{},'ru':{},'hi':{},'bn':{}
}

# Compact translations for UK/RU/HI/BN.
P['uk']={
'fora-de-portugal.html':('Я ще перебуваю за межами Португалії','Перед поїздкою оберіть шлях в’їзду, який відповідає вашій реальній меті: робота, навчання, самозайнятість, власні доходи, дистанційна робота, висококваліфікована діяльність або інша законна підстава.'),
'ue-familiares.html':('Я громадянин ЄС/ЄЕЗ/Швейцарії або член сім’ї','Громадяни ЄС/ЄЕЗ/Швейцарії та певні члени їхніх сімей користуються режимом вільного пересування, відмінним від правил для громадян третіх країн.'),
'pais-terceiro.html':('Я громадянин третьої країни','Ця категорія охоплює різні шляхи: роботу, навчання, сім’ю, CPLP, власні доходи, дистанційну роботу та інші підстави.'),
'cplp.html':('Я громадянин країни CPLP','Дозвіл CPLP має окремі правила щодо візи, запису та видачі документа на проживання.'),
'trabalho.html':('Я хочу працювати в Португалії','Наймана праця, пошук роботи, сезонна робота, самозайнятість, дистанційна робота та висококваліфікована діяльність — це різні процедури.'),
'independente-empreendedor.html':('Я самозайнятий або підприємець','Самозайнятість може ґрунтуватися на послугах, професійній діяльності або бізнесі. Для осіб за межами Португалії може діяти окремий візовий шлях.'),
'nomada-digital.html':('Я працюю дистанційно для закордонного роботодавця','Існує шлях проживання для професійної діяльності, що виконується дистанційно для осіб або компаній за межами Португалії.'),
'altamente-qualificado.html':('Я висококваліфікований фахівець','Загальний режим, Блакитна карта ЄС і Tech Visa є різними механізмами. Важливі профіль, контракт, роботодавець і кваліфікації.'),
'estudantes.html':('Я планую навчання, дослідження або стажування','Вища освіта, обмін, стажування, волонтерство та дослідження можуть підпадати під різні правила залежно від програми й тривалості.'),
'rendimentos-proprios.html':('Я пенсіонер або живу за рахунок власних доходів','У Португалії існує візовий шлях для пенсіонерів, певних релігійних осіб та людей, які живуть за рахунок власних доходів.'),
'familia.html':('Я хочу возз’єднатися або жити з родиною','Сімейний шлях залежить від громадянства та права на проживання основної особи, а також від того, де перебуває член сім’ї.'),
'investimento.html':('Я інвестор / заявник ARI','Дозвіл на проживання за інвестиції — це окремий режим, який не слід плутати зі звичайними шляхами через роботу чи підприємництво.'),
'asilo.html':('Я хочу попросити притулок / міжнародний захист','Притулок не є робочою візою чи звичайним дозволом на проживання. Це окрема процедура міжнародного захисту.'),
'protecao-temporaria.html':('Я маю тимчасовий захист / був переміщений з України','Тимчасовий захист для переміщених з України має окремі правила щодо права, реєстрації, документів і переходу.'),
'longa-duracao.html':('Я законно живу в Португалії кілька років','Статус довгострокового резидента є окремим режимом. Для громадян ЄС передбачені інші документи постійного проживання.'),
'situacoes-especiais.html':('У мене особлива або вразлива ситуація','Неповнолітні, жертви торгівлі людьми, гуманітарні випадки та інші виняткові ситуації мають окремі правила.'),
'integracao.html':('Я вже живу в Португалії й хочу організувати інтеграцію','Після міграційних документів практичне життя охоплює роботу, охорону здоров’я, податки, соціальне забезпечення, школу, кваліфікації, португальську мову, житло та місцеву підтримку.')}
P['ru']={k:(v[0].replace('Я ще перебуваю за межами Португалії','Я всё ещё нахожусь за пределами Португалии').replace('Я громадянин ЄС/ЄЕЗ/Швейцарії або член сім’ї','Я гражданин ЕС/ЕЭЗ/Швейцарии или член семьи').replace('Я громадянин третьої країни','Я гражданин третьей страны').replace('Я громадянин країни CPLP','Я гражданин страны CPLP').replace('Я хочу працювати в Португалії','Я хочу работать в Португалии').replace('Я самозайнятий або підприємець','Я самозанятый или предприниматель').replace('Я працюю дистанційно для закордонного роботодавця','Я работаю удалённо для иностранного работодателя').replace('Я висококваліфікований фахівець','Я высококвалифицированный специалист').replace('Я планую навчання, дослідження або стажування','Я планирую учёбу, исследование или стажировку').replace('Я пенсіонер або живу за рахунок власних доходів','Я пенсионер или живу за счёт собственных доходов').replace('Я хочу возз’єднатися або жити з родиною','Я хочу воссоединиться или жить с семьёй').replace('Я інвестор / заявник ARI','Я инвестор / заявитель ARI').replace('Я хочу попросити притулок / міжнародний захист','Я хочу попросить убежище / международную защиту').replace('Я маю тимчасовий захист / був переміщений з України','У меня временная защита / я был перемещён из Украины').replace('Я законно живу в Португалії кілька років','Я законно живу в Португалии несколько лет').replace('У мене особлива або вразлива ситуація','У меня особая или уязвимая ситуация').replace('Я вже живу в Португалії й хочу організувати інтеграцію','Я уже живу в Португалии и хочу организовать интеграцию'), v[1]) for k,v in P['uk'].items()}
P['hi']={
'fora-de-portugal.html':('मैं अभी पुर्तगाल के बाहर हूँ','यात्रा से पहले ऐसा प्रवेश मार्ग चुनें जो आपके वास्तविक उद्देश्य से मेल खाता हो: काम, पढ़ाई, स्वरोज़गार, अपनी आय, रिमोट काम, उच्च-कुशल गतिविधि या कोई अन्य वैध आधार।'),
'ue-familiares.html':('मैं EU/EEA/स्विट्ज़रलैंड का नागरिक या परिवार सदस्य हूँ','EU/EEA/स्विट्ज़रलैंड के नागरिक और कुछ परिवार सदस्य तीसरे देशों के नागरिकों से अलग मुक्त आवागमन नियमों के तहत आते हैं।'),
'pais-terceiro.html':('मैं तीसरे देश का नागरिक हूँ','इस श्रेणी में काम, पढ़ाई, परिवार, CPLP, अपनी आय, रिमोट काम और अन्य कई अलग मार्ग शामिल हैं।'),
'cplp.html':('मैं CPLP देश का नागरिक हूँ','CPLP निवास मार्ग में वीज़ा, अपॉइंटमेंट और निवास कार्ड जारी करने के अपने नियम हैं।'),
'trabalho.html':('मैं पुर्तगाल में काम करना चाहता/चाहती हूँ','नौकरी, नौकरी खोज, मौसमी काम, स्वरोज़गार, रिमोट काम और उच्च-कुशल गतिविधि अलग प्रक्रियाएँ हैं।'),
'independente-empreendedor.html':('मैं स्वरोज़गार या उद्यमी हूँ','स्वरोज़गार सेवाओं, पेशेवर गतिविधि या व्यवसाय पर आधारित हो सकता है। पुर्तगाल से बाहर रहने वालों के लिए अलग वीज़ा मार्ग हो सकता है।'),
'nomada-digital.html':('मैं विदेश के लिए रिमोट काम करता/करती हूँ','पुर्तगाल के बाहर स्थित व्यक्ति या संस्था के लिए रिमोट पेशेवर गतिविधि हेतु एक निवास मार्ग उपलब्ध है।'),
'altamente-qualificado.html':('मैं उच्च-कुशल पेशेवर हूँ','सामान्य मार्ग, EU ब्लू कार्ड और Tech Visa अलग व्यवस्थाएँ हैं। प्रोफ़ाइल, अनुबंध, नियोक्ता और योग्यता महत्वपूर्ण हैं।'),
'estudantes.html':('मैं पढ़ाई, शोध या इंटर्नशिप करने जा रहा/रही हूँ','उच्च शिक्षा, एक्सचेंज, इंटर्नशिप, स्वयंसेवा और शोध पर कार्यक्रम और अवधि के अनुसार अलग नियम लागू हो सकते हैं।'),
'rendimentos-proprios.html':('मैं सेवानिवृत्त हूँ या अपनी आय से जीवनयापन करता/करती हूँ','पुर्तगाल में सेवानिवृत्त लोगों, कुछ धार्मिक व्यक्तियों और अपनी आय पर रहने वालों के लिए निवास वीज़ा मार्ग है।'),
'familia.html':('मैं परिवार से मिलना या साथ रहना चाहता/चाहती हूँ','परिवार मार्ग मुख्य व्यक्ति की राष्ट्रीयता और निवास अधिकार तथा परिवार सदस्य के स्थान पर निर्भर करता है।'),
'investimento.html':('मैं निवेशक / ARI आवेदक हूँ','निवेश आधारित निवास अनुमति एक विशेष व्यवस्था है और इसे सामान्य नौकरी या उद्यमी मार्ग से नहीं मिलाना चाहिए।'),
'asilo.html':('मैं शरण / अंतरराष्ट्रीय संरक्षण माँगना चाहता/चाहती हूँ','शरण कोई काम का वीज़ा या सामान्य निवास अनुमति नहीं है। यह अंतरराष्ट्रीय संरक्षण की अलग प्रक्रिया है।'),
'protecao-temporaria.html':('मेरे पास अस्थायी संरक्षण है / मैं यूक्रेन से विस्थापित हूँ','यूक्रेन से विस्थापित लोगों के अस्थायी संरक्षण में पात्रता, पंजीकरण, दस्तावेज़ और संक्रमण के विशेष नियम हैं।'),
'longa-duracao.html':('मैं कई वर्षों से पुर्तगाल में कानूनी रूप से रह रहा/रही हूँ','दीर्घकालिक निवासी का दर्जा एक अलग व्यवस्था है। EU नागरिकों के लिए अलग स्थायी निवास दस्तावेज़ होते हैं।'),
'situacoes-especiais.html':('मेरी स्थिति विशेष या संवेदनशील है','नाबालिगों, मानव तस्करी के पीड़ितों, मानवीय मामलों और अन्य अपवादों के लिए अलग नियम लागू हो सकते हैं।'),
'integracao.html':('मैं पहले से पुर्तगाल में रहता/रहती हूँ और अपनी एकीकरण प्रक्रिया व्यवस्थित करना चाहता/चाहती हूँ','माइग्रेशन दस्तावेज़ों के बाद व्यावहारिक जीवन में काम, स्वास्थ्य, कर, सामाजिक सुरक्षा, स्कूल, योग्यताएँ, पुर्तगाली भाषा, आवास और स्थानीय सहायता शामिल हैं।')}
P['bn']={
'fora-de-portugal.html':('আমি এখনো পর্তুগালের বাইরে আছি','ভ্রমণের আগে এমন প্রবেশপথ বেছে নিন যা আপনার প্রকৃত উদ্দেশ্যের সঙ্গে মেলে: কাজ, পড়াশোনা, স্বনিয়োজিত কাজ, নিজস্ব আয়, রিমোট কাজ, উচ্চ দক্ষতার কাজ বা অন্য কোনো বৈধ ভিত্তি।'),
'ue-familiares.html':('আমি EU/EEA/সুইজারল্যান্ডের নাগরিক বা পরিবারের সদস্য','EU/EEA/সুইজারল্যান্ডের নাগরিক এবং নির্দিষ্ট পরিবারের সদস্যরা তৃতীয় দেশের নাগরিকদের থেকে ভিন্ন মুক্ত চলাচল ব্যবস্থার আওতায় পড়েন।'),
'pais-terceiro.html':('আমি তৃতীয় দেশের নাগরিক','এই শ্রেণিতে কাজ, পড়াশোনা, পরিবার, CPLP, নিজস্ব আয়, রিমোট কাজসহ বিভিন্ন পথ রয়েছে।'),
'cplp.html':('আমি CPLP দেশের নাগরিক','CPLP বাসস্থান পথে ভিসা, অ্যাপয়েন্টমেন্ট এবং রেসিডেন্স কার্ড ইস্যুর নিজস্ব নিয়ম রয়েছে।'),
'trabalho.html':('আমি পর্তুগালে কাজ করতে চাই','চাকরি, চাকরি খোঁজা, মৌসুমি কাজ, স্বনিয়োজিত কাজ, রিমোট কাজ এবং উচ্চ দক্ষতার কাজ আলাদা প্রক্রিয়া।'),
'independente-empreendedor.html':('আমি স্বনিয়োজিত বা উদ্যোক্তা','স্বনিয়োজিত কাজ সেবা, পেশাগত কার্যক্রম বা ব্যবসার ওপর ভিত্তি করে হতে পারে। পর্তুগালের বাইরে থাকা ব্যক্তিদের জন্য আলাদা ভিসা পথ থাকতে পারে।'),
'nomada-digital.html':('আমি বিদেশের জন্য রিমোট কাজ করি','পর্তুগালের বাইরে অবস্থিত ব্যক্তি বা প্রতিষ্ঠানের জন্য দূর থেকে পেশাগত কাজের জন্য একটি বাসস্থান পথ রয়েছে।'),
'altamente-qualificado.html':('আমি উচ্চ দক্ষতাসম্পন্ন পেশাজীবী','সাধারণ পথ, EU Blue Card এবং Tech Visa আলাদা ব্যবস্থা। প্রোফাইল, চুক্তি, নিয়োগকর্তা ও যোগ্যতা গুরুত্বপূর্ণ।'),
'estudantes.html':('আমি পড়াশোনা, গবেষণা বা ইন্টার্নশিপ করব','উচ্চশিক্ষা, বিনিময়, ইন্টার্নশিপ, স্বেচ্ছাসেবা ও গবেষণায় প্রোগ্রাম ও সময়কাল অনুযায়ী আলাদা নিয়ম থাকতে পারে।'),
'rendimentos-proprios.html':('আমি অবসরপ্রাপ্ত বা নিজস্ব আয়ে জীবনযাপন করি','পর্তুগালে অবসরপ্রাপ্ত ব্যক্তি, নির্দিষ্ট ধর্মীয় ব্যক্তি এবং নিজস্ব আয়ে জীবনযাপনকারীদের জন্য বাসস্থান ভিসা পথ রয়েছে।'),
'familia.html':('আমি পরিবারের সঙ্গে মিলিত হতে বা থাকতে চাই','পরিবারের পথ মূল ব্যক্তির জাতীয়তা ও বাসস্থান অধিকার এবং পরিবারের সদস্য কোথায় আছেন তার ওপর নির্ভর করে।'),
'investimento.html':('আমি বিনিয়োগকারী / ARI আবেদনকারী','বিনিয়োগভিত্তিক বাসস্থান অনুমতি একটি বিশেষ ব্যবস্থা এবং সাধারণ চাকরি বা উদ্যোক্তা পথের সঙ্গে গুলিয়ে ফেলা উচিত নয়।'),
'asilo.html':('আমি আশ্রয় / আন্তর্জাতিক সুরক্ষা চাই','আশ্রয় কাজের ভিসা বা সাধারণ বাসস্থান অনুমতি নয়। এটি আন্তর্জাতিক সুরক্ষার আলাদা প্রক্রিয়া।'),
'protecao-temporaria.html':('আমার অস্থায়ী সুরক্ষা আছে / আমি ইউক্রেন থেকে বাস্তুচ্যুত','ইউক্রেন থেকে বাস্তুচ্যুত মানুষের অস্থায়ী সুরক্ষায় যোগ্যতা, নিবন্ধন, নথি ও পরিবর্তনের বিশেষ নিয়ম রয়েছে।'),
'longa-duracao.html':('আমি কয়েক বছর ধরে পর্তুগালে আইনগতভাবে বসবাস করছি','দীর্ঘমেয়াদি বাসিন্দার মর্যাদা আলাদা ব্যবস্থা। EU নাগরিকদের জন্য পৃথক স্থায়ী বাসস্থান নথি রয়েছে।'),
'situacoes-especiais.html':('আমার বিশেষ বা ঝুঁকিপূর্ণ পরিস্থিতি আছে','অপ্রাপ্তবয়স্ক, মানবপাচারের শিকার, মানবিক পরিস্থিতি এবং অন্যান্য ব্যতিক্রমী ক্ষেত্রে আলাদা নিয়ম প্রযোজ্য।'),
'integracao.html':('আমি ইতিমধ্যে পর্তুগালে থাকি এবং একীভূত হওয়ার কাজগুলো সংগঠিত করতে চাই','অভিবাসন নথির পর বাস্তব জীবনে কাজ, স্বাস্থ্য, কর, সামাজিক নিরাপত্তা, স্কুল, যোগ্যতা, পর্তুগিজ ভাষা, বাসস্থান ও স্থানীয় সহায়তা অন্তর্ভুক্ত।')}

OFFICIAL=[('AIMA','https://aima.gov.pt/'),('gov.pt','https://www.gov.pt/'),('Justiça','https://justica.gov.pt/'),('Segurança Social','https://www.seg-social.pt/')]

def source_ids(page):
 try: data=json.loads(SOURCE_CFG.read_text(encoding='utf-8'))
 except Exception: return []
 out=[]
 for s in data.get('sources',[]):
  pages=set(s.get('pages',[]))
  if page in pages or f'en/{page}' in pages: out.append(s.get('id'))
 return sorted(x for x in set(out) if x)

def page_html(locale,page,title,lead):
 c=COMMON[locale]; ids=source_ids(page)
 meta=f'<meta name="official-source-ids" content="{html.escape(" ".join(ids))}">' if ids else ''
 cards=''.join(f'<article class="card"><h3>{html.escape(a)}</h3><p>{html.escape(b)}</p></article>' for a,b in c['cards'])
 official=''.join(f'<a class="card" href="{u}" target="_blank" rel="noopener"><h3>{html.escape(n)}</h3><p>{html.escape(c["source"])}</p></a>' for n,u in OFFICIAL)
 return f'''<!doctype html><html lang="{locale}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#09315c"><meta name="description" content="{html.escape(lead,quote=True)}"><meta name="last-reviewed" content="{REVIEW_ISO}"><meta name="robots" content="noindex,nofollow"><title>{html.escape(title)} | Guia Migrante PT</title><link rel="canonical" href="{BASE}/{locale}/{page}"><link rel="alternate" hreflang="pt-PT" href="{BASE}/{page}"><link rel="alternate" hreflang="en" href="{BASE}/en/{page}"><link rel="icon" href="../favicon.png"><link rel="stylesheet" href="../locale-core.css"><link rel="stylesheet" href="../language-switcher.css">{meta}</head><body><a class="skip-link" href="#content">{html.escape(c['section'])}</a><div class="topbar"><div class="container">{html.escape(c['ind'])} · {html.escape(c['checked'])}</div></div><header><div class="container header-inner"><a class="brand" href="index.html"><img src="../logo-guia-migrante-256.png" alt=""><span><strong>Guia Migrante PT</strong><small>{html.escape(c['brand'])}</small></span></a><nav class="desktop-nav"><a href="percursos.html">{html.escape(c['routes'])}</a><a href="contactos.html">{html.escape(c['contacts'])}</a></nav><div class="header-actions"><button class="menu-btn" id="menuButton" type="button" aria-expanded="false" aria-controls="mobileNav">☰</button></div></div><nav class="mobile-nav" id="mobileNav"><a href="percursos.html">{html.escape(c['routes'])}</a><a href="contactos.html">{html.escape(c['contacts'])}</a></nav></header><div class="brand-stripe"></div><div class="review-strip"><div class="container"><span class="review-badge">{html.escape(c['stage'])}</span></div></div><main id="content"><section class="hero"><div class="container"><div class="breadcrumbs">Guia Migrante PT · {html.escape(c['routes'])}</div><span class="kicker">{html.escape(c['routes'])}</span><h1>{html.escape(title)}</h1><p>{html.escape(lead)}</p><div class="hero-actions"><a class="btn primary" href="percursos.html">{html.escape(c['routes'])}</a><a class="btn secondary" href="contactos.html">{html.escape(c['contacts'])}</a></div><div class="notice">{html.escape(c['stage'])}</div></div></section><section class="content"><div class="container"><div class="section-head"><h2>{html.escape(c['section'])}</h2><p>{html.escape(c['intro'])}</p></div><div class="grid three">{cards}</div></div></section><section class="content white"><div class="container"><div class="section-head"><h2>{html.escape(c['official'])}</h2><p>{html.escape(c['checked'])}</p></div><div class="grid three">{official}</div></div></section></main><footer><div class="container footer-bottom"><span>© 2026 Guia Migrante PT</span><span>{html.escape(c['legal'])}</span></div></footer><script>const b=document.getElementById('menuButton'),n=document.getElementById('mobileNav');if(b&&n)b.addEventListener('click',()=>{{const o=n.classList.toggle('open');b.setAttribute('aria-expanded',String(o));}});</script><script src="../language-switcher.js" defer></script></body></html>'''

def main():
 total=0
 for loc in COMMON:
  target=SITE/loc; target.mkdir(exist_ok=True)
  missing=[p for p in ROUTES if p not in P[loc]]
  if missing: raise SystemExit(f'{loc}: missing translations {missing}')
  for page in ROUTES:
   title,lead=P[loc][page]
   (target/page).write_text(page_html(loc,page,title,lead),encoding='utf-8'); total+=1
 print(f'Built staged migration-route translations: {total} pages across {len(COMMON)} locales')

if __name__=='__main__': main()
