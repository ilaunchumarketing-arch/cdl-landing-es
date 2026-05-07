#!/usr/bin/env python3
"""Translate the Spanish CDL landing page to English and Portuguese.

Run from the cdl-landing-es directory:
  python3 translate-site.py

Reads: ./index.html
Writes: ../cdl-landing-new-en/index.html, ../cdl-landing-pt/index.html
"""
import re
from pathlib import Path

SRC = Path(__file__).parent / "index.html"
EN_DST = Path(__file__).parent.parent / "cdl-landing-new-en" / "index.html"
PT_DST = Path(__file__).parent.parent / "cdl-landing-pt" / "index.html"

# ============================================================
# ENGLISH DICTIONARY — ordered longest-first to avoid partial matches
# ============================================================
EN = {
    # Meta + title
    "Escuela CDL en Tampa, FL | Clase A en 4 Semanas | CDL Training of Tampa":
        "CDL School in Tampa, FL | Class A in 4 Weeks | CDL Training of Tampa",
    "Escuela CDL Clase A en Tampa, FL. Certificada FMCSA ELDT. Instrucción 1-a-1 en español. 4 semanas. Desde $3,000 — examen incluido. Colocación laboral real.":
        "Class A CDL school in Tampa, FL. FMCSA ELDT certified. Bilingual 1-on-1 instruction. 4 weeks. From $3,000 — exam included. Real job placement.",
    "escuela CDL Tampa, CDL Clase A Florida, ELDT en español, CDL en 4 semanas, camionero Tampa, licencia CDL Florida, entrenamiento camionero, CDL training Tampa":
        "CDL school Tampa, Class A CDL Florida, ELDT training, CDL in 4 weeks, Tampa trucker, Florida CDL license, truck driver training, CDL training Tampa",

    # OG/Twitter
    "Escuela CDL en Tampa, FL | Clase A en 4 Semanas":
        "CDL School in Tampa, FL | Class A in 4 Weeks",
    "Escuela CDL Clase A certificada FMCSA ELDT en Tampa. Instrucción 1-a-1 en español. Desde $3,000 todo incluido. Colocación laboral.":
        "FMCSA ELDT certified Class A CDL school in Tampa. 1-on-1 bilingual instruction. From $3,000 all-inclusive. Real job placement.",
    "Escuela CDL certificada FMCSA ELDT en Tampa. Instrucción bilingüe 1-a-1. Desde $3,000. Colocación laboral.":
        "FMCSA ELDT certified CDL school in Tampa. Bilingual 1-on-1 instruction. From $3,000. Real job placement.",

    # Schema LocalBusiness description
    "Escuela CDL Clase A aprobada por el estado en Tampa, FL. Entrenamiento ELDT certificado por FMCSA. Instrucción 1-a-1 en español. 4 semanas. Colocación laboral.":
        "State-approved Class A CDL school in Tampa, FL. FMCSA-certified ELDT training. Bilingual 1-on-1 instruction. 4 weeks. Real job placement.",

    # Schema Course
    "CDL Clase A — Entrenamiento ELDT Completo":
        "Class A CDL — Complete ELDT Training",
    "Programa de entrenamiento CDL Clase A de 160 horas. Incluye curso teórico ELDT, entrenamiento práctico 1-a-1, examen CDL, y apoyo de colocación laboral. Instructores bilingües.":
        "160-hour Class A CDL training program. Includes ELDT theory coursework, hands-on 1-on-1 training, CDL exam, and job placement support. Bilingual instructors.",
    "CDL Clase A — Automático": "Class A CDL — Automatic",
    "CDL Clase A — Manual": "Class A CDL — Manual",

    # FAQ Schema questions
    "¿Necesito experiencia previa para inscribirme?":
        "Do I need prior experience to enroll?",
    "No. Solo necesitas una licencia de conducir válida, tener 18 años o más (21+ para manejar entre estados), pasar un examen físico DOT y una prueba de drogas. Aceptamos principiantes completos.":
        "No. You just need a valid driver license, be 18 or older (21+ for interstate driving), pass a DOT physical and a drug test. Complete beginners are welcome.",
    "¿Qué incluye exactamente el precio de $3,000?":
        "What exactly does the $3,000 price include?",
    "Todo: curso teórico ELDT de 160 horas, cuota del examen CDL, todas las horas de entrenamiento práctico en camión real, inspección pre-viaje, y apoyo de colocación laboral. Sin costos ocultos.":
        "Everything: 160-hour ELDT theory course, CDL exam fee, all hands-on training hours in real trucks, pre-trip inspection training, and job placement support. No hidden costs.",
    "¿Ofrecen financiamiento o planes de pago?":
        "Do you offer financing or payment plans?",
    "Sí. Trabajamos con socios de financiamiento. Un asesor revisa tus opciones durante la consulta gratuita.":
        "Yes. We work with financing partners. An advisor reviews your options during the free consultation.",
    "¿Cuándo empieza la próxima clase?":
        "When does the next class start?",
    "Inscribimos de forma continua debido a los cupos limitados para instrucción 1-a-1. Contacta hoy para verificar la próxima fecha disponible.":
        "We enroll on a rolling basis because of limited 1-on-1 spots. Contact us today to check the next available start date.",
    "¿Cuál es la diferencia entre Automático y Manual?":
        "What's the difference between Automatic and Manual?",
    "El Automático ($3,000) es más fácil de aprender y cubre la mayoría de empleos. El Manual ($3,500) te da un CDL sin restricciones — puedes manejar cualquier camión, lo que significa más opciones de trabajo y mayor paga.":
        "Automatic ($3,000) is easier to learn and covers most jobs. Manual ($3,500) gives you an unrestricted CDL — you can drive any truck, which means more job options and higher pay.",
    "¿Qué es ELDT y por qué importa?":
        "What is ELDT and why does it matter?",
    "ELDT (Entry-Level Driver Training) es el entrenamiento obligatorio que FMCSA exige desde febrero 2022 para cualquier persona que obtenga un CDL Clase A o B por primera vez. Solo escuelas registradas en el Training Provider Registry (TPR) de FMCSA pueden certificarte. Nosotros estamos registrados.":
        "ELDT (Entry-Level Driver Training) is the mandatory training FMCSA has required since February 2022 for anyone getting a Class A or B CDL for the first time. Only schools registered in FMCSA's Training Provider Registry (TPR) can certify you. We are registered.",
    "¿Necesito hablar inglés perfecto por la regla ELP?":
        "Do I need to speak perfect English because of the ELP rule?",
    "No necesitas ser nativo. La regla ELP (vigente desde junio 2025) requiere que puedas comunicarte funcionalmente en inglés con autoridades, leer señales de tránsito, y llenar reportes básicos. Nuestros instructores bilingües te preparan específicamente para esto.":
        "You don't need to be a native speaker. The ELP rule (effective June 2025) requires that you can communicate functionally in English with law enforcement, read traffic signs, and fill out basic reports. Our bilingual instructors prepare you specifically for this.",
    "¿Qué documentos necesito para inscribirme?":
        "What documents do I need to enroll?",
    "Licencia de conducir FL válida, tarjeta de seguro social o ITIN, prueba de residencia en Florida, examen médico DOT certificado (MCSA-5875), y prueba de drogas. Te ayudamos con el proceso.":
        "Valid Florida driver license, Social Security card or ITIN, proof of Florida residency, certified DOT medical exam (MCSA-5875), and drug test. We help you through the process.",
    "¿Cuánto voy a ganar después de graduarme?":
        "How much will I earn after graduating?",
    "Conductores nuevos en Tampa ganan $55,000–$65,000 el primer año (OTR). Rutas regionales del sureste pagan $1,400–$1,800/semana ($72,800–$93,600/año). Conductores locales con experiencia: $65,000–$85,000. Rutas intermodales del Puerto de Tampa pagan 20–30% más.":
        "New Tampa drivers earn $55,000–$65,000 their first year (OTR). Southeast regional routes pay $1,400–$1,800/week ($72,800–$93,600/year). Experienced local drivers: $65,000–$85,000. Intermodal routes from the Port of Tampa pay 20–30% more.",
    "¿Un DUI o récord criminal me descalifica?":
        "Does a DUI or criminal record disqualify me?",
    "Depende de la gravedad y cuánto tiempo haya pasado. Un DUI reciente puede ser descalificante; uno antiguo puede no serlo. Habla honestamente con un asesor — revisamos tu caso específico sin juzgar.":
        "It depends on the severity and how long ago it was. A recent DUI may be disqualifying; an older one may not be. Talk honestly with an advisor — we review your specific case without judgment.",
    "¿Qué pasa en el examen físico DOT?":
        "What happens in the DOT physical exam?",
    "Un examinador médico certificado revisa visión (20/40 corregida), audición, presión arterial, diabetes, y condiciones cardíacas. Dura 30-45 minutos. Emite tarjeta MCSA-5875 válida por 2 años (o 1 año si tienes condiciones monitoreadas).":
        "A certified medical examiner checks vision (20/40 corrected), hearing, blood pressure, diabetes, and heart conditions. Takes 30–45 minutes. Issues the MCSA-5875 card valid for 2 years (or 1 year if you have monitored conditions).",

    # Alt tags
    "Instructor bilingüe enseñando inspección pre-viaje a estudiante dentro de cabina de camión Clase A en Tampa":
        "Bilingual instructor teaching pre-trip inspection to student inside Class A truck cabin in Tampa",
    "Camión Clase A en autopista de Florida al atardecer con palmeras al horizonte":
        "Class A truck on Florida highway at sunset with palm trees on the horizon",
    "Vista desde cabina de camión Clase A en autopista de Florida de noche con luces y señales":
        "View from Class A truck cabin on Florida highway at night with lights and signs",
    "Licencia CDL Clase A de Florida sobre escritorio con mapa y llaves de camión":
        "Florida Class A CDL license on desk with map and truck keys",
    "Chofer hispano en inspección de carretera del Florida Highway Patrol":
        "Hispanic driver at Florida Highway Patrol roadside inspection",
    "Mapa de Florida con formulario médico DOT y documentos regulatorios CDL":
        "Florida map with DOT medical form and CDL regulatory documents",
    "Instructor explicando inspección pre-viaje a estudiante de CDL":
        "Instructor explaining pre-trip inspection to CDL student",
    "Carlos Alejandro Ortega Garcia — Graduado CDL Training of Tampa":
        "Carlos Alejandro Ortega Garcia — CDL Training of Tampa Graduate",
    "Anthony Lewis Friend — Graduado CDL Training of Tampa":
        "Anthony Lewis Friend — CDL Training of Tampa Graduate",
    "Alex Antonio Sepulveda Rosado — Graduado CDL Training of Tampa":
        "Alex Antonio Sepulveda Rosado — CDL Training of Tampa Graduate",
    "Graduados de CDL Training of Tampa con instructores":
        "CDL Training of Tampa graduates with instructors",

    # URGENT BAR + NAV
    "INSCRIPCIONES ABIERTAS — CUPOS LIMITADOS ESTE MES":
        "ENROLLMENT OPEN — LIMITED SPOTS THIS MONTH",
    "Navegación principal": "Main navigation",
    "Enlaces principales": "Main links",
    "Por Qué Nosotros": "Why Choose Us",
    "Seleccionar idioma": "Select language",
    "Inscríbete Ahora": "Enroll Now",

    # HERO
    "Aprobado por el Estado · Certificado FMCSA ELDT":
        "State Approved · FMCSA ELDT Certified",
    "Obtén Tu": "Get Your",
    "CDL en": "CDL in",
    "4 Semanas.": "4 Weeks.",
    "Gana $1,400–$1,800/Semana en Tampa":
        "Earn $1,400–$1,800/Week in Tampa",
    "La escuela CDL #1 de Tampa desde 2019. Instrucción 1-a-1 en español. Certificada FMCSA ELDT. Examen incluido. Colocación laboral real con empresas que contratan ahora.":
        "Tampa's #1 CDL school since 2019. Bilingual 1-on-1 instruction. FMCSA ELDT certified. CDL exam included. Real job placement with companies hiring now.",
    "Sin costos ocultos.": "No hidden costs.",
    "47+ Graduados Activos": "47+ Active Graduates",
    "4.9★ en Google": "4.9★ on Google",
    "Se Habla Español": "Bilingual Support",
    "Entrenamiento 1-a-1": "1-on-1 Training",
    "Escasez de 80,000 choferes en EE.UU. — demanda récord":
        "80,000 US driver shortage — record demand",
    "Empezar Gratis": "Start Free",

    # LEAD FORM
    "Reserva Tu": "Reserve Your",
    "Cupo": "Spot",
    "Consulta gratis.": "Free consultation.",
    "Sin compromiso.": "No obligation.",
    "Inscripción mensual": "Monthly enrollment",
    "Solo 5 cupos disponibles": "Only 5 spots available",
    "Nombre": "First Name",
    "Apellido": "Last Name",
    "Teléfono": "Phone",
    "Correo electrónico": "Email",
    "Programa": "Program",
    "Número de teléfono": "Phone number",
    "Selecciona tu programa...": "Select your program...",
    "CDL Clase A — Automático · $3,000": "Class A CDL — Automatic · $3,000",
    "CDL Clase A — Manual · $3,500": "Class A CDL — Manual · $3,500",
    "No estoy seguro — necesito más información":
        "Not sure — I need more information",
    "Obtener Información Gratis →": "Get Free Info →",
    "Privado y Seguro · Sin Spam · Nunca Vendido":
        "Private & Secure · No Spam · Never Sold",
    "Completa todos los campos": "Please complete all fields",
    "Enviando...": "Sending...",
    "✓ ¡Te Llamamos en Menos de 24 Horas!":
        "✓ We'll Call You Within 24 Hours!",
    "Algo salió mal — intenta de nuevo":
        "Something went wrong — please try again",
    "Interés Desconocido": "Unknown Interest",

    # TRUST STRIP
    "Indicadores de confianza": "Trust indicators",
    "Registrado en FMCSA TPR": "Registered in FMCSA TPR",
    "Licencia Comisión Educación FL": "FL Education Commission Licensed",
    "Instrucción 1-a-1": "1-on-1 Instruction",
    "Colocación Laboral Real": "Real Job Placement",
    "Instructores Bilingües": "Bilingual Instructors",
    "Negocio Familiar · Desde 2019": "Family-Owned · Since 2019",

    # PROGRAMS
    "Elige Tu Programa": "Choose Your Program",
    "TODO INCLUIDO.": "ALL-INCLUSIVE.",
    "Sin Costos Ocultos. Jamás.": "No Hidden Costs. Ever.",
    "Un precio fijo. Examen CDL, curso ELDT, entrenamiento práctico y colocación laboral — todo incluido.":
        "One flat price. CDL exam, ELDT coursework, hands-on training, and job placement — all included.",
    "Más Popular": "Most Popular",
    "CDL Clase A": "Class A CDL",
    "Transmisión Automática · El Camino Más Rápido":
        "Automatic Transmission · The Fastest Path",
    " todo incluido": " all-inclusive",
    "Curso ELDT de 160 Horas — Incluido": "160-Hour ELDT Course — Included",
    "Examen CDL — Incluido": "CDL Exam — Included",
    "Entrenamiento Práctico en Camión Real": "Hands-On Training in a Real Truck",
    "Entrenamiento de Inspección Pre-Viaje": "Pre-Trip Inspection Training",
    "Apoyo de Colocación Laboral": "Job Placement Support",
    "Entrenamiento Lun–Vie Tiempo Completo": "Mon–Fri Full-Time Training",
    "Inscríbete — $3,000 →": "Enroll — $3,000 →",
    "Inscríbete — $3,500 →": "Enroll — $3,500 →",
    "Máxima Flexibilidad": "Maximum Flexibility",
    "Transmisión Manual · Sin Restricciones en la Licencia":
        "Manual Transmission · No License Restrictions",
    "Todo lo del Automático, más:": "Everything in Automatic, plus:",
    "Sin Restricción de Transmisión": "No Transmission Restriction",
    "Maneja Cualquier Camión, En Cualquier Lugar":
        "Drive Any Truck, Anywhere",
    "Mayor Potencial de Ingresos": "Higher Income Potential",
    "Entrenamiento en Carretera y Patio": "Road and Yard Training",
    "Máxima Flexibilidad de Carrera": "Maximum Career Flexibility",

    # WHY US
    "ESCUELA CDL EN TAMPA": "CDL SCHOOL IN TAMPA",
    "QUE SÍ TE ENSEÑA.": "THAT ACTUALLY TEACHES YOU.",
    "No somos una fábrica de graduados. Somos una escuela familiar con instructores bilingües que se aseguran de que pases el examen — y consigas empleo — a la primera.":
        "We're not a graduate factory. We're a family-owned school with bilingual instructors who make sure you pass the exam — and land the job — on the first try.",
    "Sin clases masivas. Un instructor, un estudiante, un camión. Aprendes más rápido y retienes lo que importa para el examen.":
        "No huge classes. One instructor, one student, one truck. You learn faster and retain what matters for the exam.",
    "Entrenamiento en español con vocabulario técnico en inglés. Te preparamos para pasar la regla ELP con confianza.":
        "Bilingual training with English technical vocabulary. We prepare you to pass the ELP rule with confidence.",
    "Camiones Reales · Patio Real": "Real Trucks · Real Training Yard",
    "Entrenas en el mismo tipo de camión que vas a manejar. Patio privado con obstáculos reales para maniobras de examen.":
        "You train in the same type of truck you'll drive on the job. Private training yard with real obstacles for exam maneuvers.",
    "Certificado FMCSA ELDT": "FMCSA ELDT Certified",
    "Registrados oficialmente en el Training Provider Registry (TPR) de FMCSA. Solo estas escuelas pueden certificarte legalmente para CDL.":
        "Officially registered in FMCSA's Training Provider Registry (TPR). Only these schools can legally certify you for a CDL.",
    "Licenciado por el Estado de FL": "Florida State Licensed",
    "Licencia oficial de la Comisión para la Educación Independiente de Florida. Cumplimos con todos los estándares del Departamento de Educación.":
        "Official license from the Florida Commission for Independent Education. We meet every Department of Education standard.",
    "Conexiones directas con transportistas que contratan en Tampa, Florida y el sureste. Te ayudamos a conseguir tu primer empleo antes de graduarte.":
        "Direct connections with carriers hiring in Tampa, Florida, and the Southeast. We help you land your first job before graduation.",

    # SALARIES
    "La Realidad del Salario": "The Real Income Data",
    "TU NUEVO SUELDO": "YOUR NEW PAYCHECK",
    "EN 4 SEMANAS.": "IN 4 WEEKS.",
    "Estos son los números reales del mercado de Tampa en 2026. No promesas vacías — datos verificables de BLS, la industria, y las ofertas actuales de empresas que contratan graduados como los nuestros.":
        "These are the real 2026 Tampa market numbers. No empty promises — verifiable data from BLS, the industry, and current offers from companies hiring graduates like ours.",
    "Primer Año OTR": "First-Year OTR",
    "Conductor nuevo, rutas de larga distancia (Over-The-Road).":
        "New driver, Over-The-Road long-haul routes.",
    "Fuente: BLS 2024": "Source: BLS 2024",
    "Regional Sureste": "Southeast Regional",
    "Por semana.": "Per week.",
    "Rutas regionales Florida–Georgia–Carolinas. Home semanal.":
        "Florida–Georgia–Carolinas regional routes. Home weekly.",
    "$72K–$93K/año · Fuente: Glassdoor Tampa":
        "$72K–$93K/year · Source: Glassdoor Tampa",
    "Local Tampa": "Tampa Local",
    "Conductor local con experiencia. En casa todos los días.":
        "Experienced local driver. Home every day.",
    "Fuente: Indeed Tampa": "Source: Indeed Tampa",
    "10+ Años Tampa": "10+ Years in Tampa",
    "Promedio anual para veteranos del volante en Tampa Bay.":
        "Annual average for seasoned drivers in Tampa Bay.",
    "Fuente: Glassdoor 2026": "Source: Glassdoor 2026",
    "Ventaja Puerto de Tampa:": "Port of Tampa Advantage:",
    "Los conductores con experiencia intermodal del Puerto de Tampa ganan 20–30% más que el promedio OTR. Tampa es un punto estratégico entre el Puerto de Tampa Bay, JAXPORT y PortMiami — rutas que pocos conductores pueden trabajar.":
        "Drivers with Port of Tampa intermodal experience earn 20–30% more than OTR average. Tampa sits strategically between Port Tampa Bay, JAXPORT, and PortMiami — routes few drivers can cover.",
    "Bono Florida:": "Florida Bonus:",
    "Sin impuestos estatales sobre el ingreso. Cada dólar que ganas rinde más que en otros estados.":
        "No state income tax. Every dollar you earn goes further than in other states.",
    "Ver desglose completo de salarios →": "See full salary breakdown →",

    # CURRICULUM
    "Lo Que Aprenderás": "What You'll Learn",
    "160 HORAS. CERO FILLER.": "160 HOURS. ZERO FILLER.",
    "TODO LO QUE EL EXAMEN EXIGE.": "EVERYTHING THE EXAM DEMANDS.",
    "Nuestro currículo ELDT cubre cada tema que FMCSA requiere, más las habilidades reales que necesitas desde tu primer día en el volante.":
        "Our ELDT curriculum covers every topic FMCSA requires, plus the real-world skills you need from day one behind the wheel.",
    "Teoría FMCSA (30+ Temas)": "FMCSA Theory (30+ Topics)",
    "Regulaciones federales, Horas de Servicio (HOS), ELD, fatiga, manejo defensivo, diario de bitácora, CSA.":
        "Federal regulations, Hours of Service (HOS), ELD, fatigue, defensive driving, logbook, CSA.",
    "Inspección Pre-Viaje": "Pre-Trip Inspection",
    "Sistema de 3 puntos: motor, sistema de combustible, frenos neumáticos. El punto donde más gente pierde el examen — aquí no.":
        "3-point system: engine, fuel system, air brakes. The spot where most people fail the exam — not here.",
    "Maniobras de Patio": "Yard Maneuvers",
    "Parking recto, offset back, alley dock, parallel. Practica en patio privado hasta que sea automático.":
        "Straight line backing, offset back, alley dock, parallel. Practice in a private yard until it's automatic.",
    "Manejo en Carretera": "Road Driving",
    "Ciudad, autopista, nocturno, lluvia. Rutas reales alrededor de Tampa con tráfico real.":
        "City, highway, night, rain. Real routes around Tampa with real traffic.",
    "Preparación del Examen CDL": "CDL Exam Prep",
    "Simulacros completos del examen general, frenos de aire, y combinación. Pasas antes de pisar el DHSMV.":
        "Complete mock exams for general knowledge, air brakes, and combination. You pass before setting foot in the DHSMV.",
    "Regla ELP (Dominio del Inglés)": "ELP Rule (English Proficiency)",
    "Vocabulario CDL en inglés: señales, inspección, radio, preguntas de tránsito. Cumplimiento garantizado de la regla ELP 2025.":
        "CDL vocabulary in English: signs, inspection, radio, traffic questions. Guaranteed 2025 ELP rule compliance.",
    "Introducción a Endosos": "Intro to Endorsements",
    "HAZMAT, Tanker, Doubles/Triples, Passenger. Te mostramos cuáles valen la pena para Tampa y cómo prepararte.":
        "HAZMAT, Tanker, Doubles/Triples, Passenger. We show you which ones are worth it in Tampa and how to prepare.",
    "Preparación para la Entrevista": "Interview Prep",
    "Cómo hablar con reclutadores, qué pedir en tu primer contrato, y cómo leer tu carta de empleo (bonos, paga por milla, beneficios).":
        "How to talk to recruiters, what to ask for in your first contract, and how to read your offer letter (bonuses, cents per mile, benefits).",
    "Horas de entrenamiento ELDT certificado · Curso aprobado por FMCSA":
        "Hours of FMCSA-approved certified ELDT training",

    # CINEMATIC
    "LA CARRETERA TE": "THE ROAD IS",
    "ESTÁ ESPERANDO": "WAITING FOR YOU",
    "EN 4 SEMANAS": "IN 4 WEEKS",
    "ESTA PODRÍA SER TU VISTA.": "THIS COULD BE YOUR VIEW.",
    "Camiones en la autopista al atardecer": "Trucks on the highway at sunset",
    "Interior de cabina de camión": "Truck cabin interior",

    # GRADUATES
    "Graduados Reales": "Real Graduates",
    "SUS CARRERAS": "THEIR CAREERS",
    "EMPEZARON AQUÍ.": "STARTED HERE.",
    "Cada certificado representa una vida transformada. Estos son estudiantes reales de CDL Training of Tampa.":
        "Every certificate represents a transformed life. These are real students from CDL Training of Tampa.",
    "Graduado CDL Clase A": "Class A CDL Graduate",
    "Graduado CDL Clase A · Con Nuestros Instructores":
        "Class A CDL Graduate · With Our Instructors",

    # STEPS
    "El Proceso": "The Process",
    "DE CERO A CDL": "FROM ZERO TO CDL",
    "EN 4 PASOS.": "IN 4 STEPS.",
    "Envía Tu Información": "Send Your Info",
    "Llena el formulario. Un asesor te contacta en menos de 24 horas para responder preguntas y confirmar disponibilidad.":
        "Fill out the form. An advisor contacts you within 24 hours to answer questions and confirm availability.",
    "Elige Tu Programa": "Choose Your Program",
    "Automático ($3,000) o Manual ($3,500). Te ayudamos a decidir según tus metas profesionales.":
        "Automatic ($3,000) or Manual ($3,500). We help you decide based on your career goals.",
    "Completa el Entrenamiento": "Complete the Training",
    "4 semanas. Lun–Vie. Instrucción 1-a-1 en camiones reales. Instructores bilingües. Examen en sitio cuando estés listo.":
        "4 weeks. Mon–Fri. 1-on-1 instruction in real trucks. Bilingual instructors. On-site exam when you're ready.",
    "Consigue Empleo": "Land a Job",
    "Gradúate con tu CDL en mano. Te conectamos con las mejores empresas de camiones que contratan en Florida.":
        "Graduate with your CDL in hand. We connect you with the top trucking companies hiring in Florida.",

    # TESTIMONIALS
    "Lo Que Dicen Los Graduados": "What Graduates Say",
    "RESULTADOS REALES.": "REAL RESULTS.",
    "PERSONAS REALES.": "REAL PEOPLE.",
    "\"Ganaba $14/hora en un almacén. 4 semanas después de inscribirme ya tenía mi CDL y una oferta de trabajo de $72K. Los instructores son pacientes, profesionales y realmente se preocupan.\"":
        "\"I was earning $14/hour in a warehouse. Four weeks after enrolling I had my CDL and a $72K job offer. The instructors are patient, professional, and truly care.\"",
    "Ahora Gana $72K · Conductor OTR": "Now Earns $72K · OTR Driver",
    "\"Pasé el examen de CDL al primer intento gracias a los instructores bilingües. Conseguí trabajo inmediatamente después de graduarme. 100% lo recomiendo a cualquier hispano que quiera un futuro mejor.\"":
        "\"I passed the CDL exam on my first try thanks to the bilingual instructors. I got a job immediately after graduating. I 100% recommend this to anyone who wants a better future.\"",
    "Graduado CDL · Tampa, FL": "CDL Graduate · Tampa, FL",
    "\"La mejor inversión que hice. La instrucción 1-a-1 es diferente a cualquier otra escuela. Aprobé a la primera y tuve 3 ofertas de trabajo en una semana de graduarme.\"":
        "\"The best investment I ever made. The 1-on-1 instruction is unlike any other school. I passed on my first try and had 3 job offers within a week of graduating.\"",
    "Graduado Clase A · Contratado": "Class A Graduate · Hired",

    # BLOG CTA
    "Recursos y Guías": "Resources & Guides",
    "APRENDE ANTES DE INVERTIR.": "LEARN BEFORE YOU INVEST.",
    "INFÓRMATE.": "GET INFORMED.",
    "Artículos gratis con información real sobre CDL en Florida: costos, regulaciones, salarios y los cambios 2025 que afectan a todos los conductores hispanos.":
        "Free articles with real information on CDL in Florida: costs, regulations, salaries, and the 2025 changes affecting every driver.",
    "Cómo Obtener Tu CDL en Florida: Guía Paso a Paso 2026":
        "How to Get Your CDL in Florida: Step-by-Step Guide 2026",
    "Todo el proceso explicado: Clase A vs B, ELDT, examen médico DOT, CLP, endosos, y cuánto tarda realmente obtener tu licencia en FL.":
        "The whole process explained: Class A vs B, ELDT, DOT physical, CLP, endorsements, and how long it really takes to get your Florida license.",
    "Leer más →": "Read more →",
    "8 min lectura": "8 min read",
    "Nuevo 2025": "New 2025",
    "Regla ELP: Dominio del Inglés para Choferes CDL (Junio 2025)":
        "ELP Rule: English Proficiency for CDL Drivers (June 2025)",
    "La nueva regla federal que puede sacarte de servicio al instante. Qué dice, cómo pasas la inspección, y cómo te preparamos para cumplir.":
        "The new federal rule that can put you out of service instantly. What it says, how you pass inspection, and how we prepare you to comply.",
    "7 min lectura": "7 min read",
    "Regulaciones": "Regulations",
    "Regulaciones CDL en Florida: FMCSA, FL DHSMV y Examen Médico DOT":
        "Florida CDL Regulations: FMCSA, FL DHSMV, and DOT Physical",
    "Los requisitos exactos para tu CDL en Florida. Fees reales, tiempos de examen, y qué condiciones médicas pueden descalificarte (y cuáles no).":
        "The exact requirements for your Florida CDL. Real fees, exam timelines, and which medical conditions can disqualify you (and which don't).",
    "9 min lectura": "9 min read",
    "Ver Todos los Artículos": "View All Articles",
    "Guía": "Guide",

    # 2025 ALERT
    "Alerta · Cambios 2025 en la Industria": "Alert · 2025 Industry Changes",
    "LA INDUSTRIA CAMBIÓ.": "THE INDUSTRY CHANGED.",
    "TU OPORTUNIDAD NUNCA FUE MAYOR.": "YOUR OPPORTUNITY HAS NEVER BEEN BIGGER.",
    "Desde el <strong>25 de junio de 2025</strong>, la regla ELP (Dominio del Inglés) está en los Criterios Fuera de Servicio de CVSA. Al mismo tiempo, nuevas reglas federales están sacando a ~200,000 conductores del mercado. <strong>La demanda de choferes certificados nunca fue tan alta.</strong>":
        "As of <strong>June 25, 2025</strong>, the ELP (English Proficiency) rule is in CVSA's Out-of-Service Criteria. At the same time, new federal rules are removing ~200,000 drivers from the market. <strong>Demand for certified drivers has never been higher.</strong>",
    "Escasez de conductores EE.UU. 2025": "US driver shortage 2025",
    "Empleos de camión activos en Tampa ahora": "Active trucking jobs in Tampa right now",
    "Aumento de pago al conductor desde 2016 (ajustado)":
        "Driver pay increase since 2016 (inflation-adjusted)",
    "¿Hablas español y te preocupa la regla ELP? <strong>Relájate.</strong> Nuestros instructores bilingües te enseñan específicamente el vocabulario CDL en inglés — señales de tránsito, inspecciones, comunicación con autoridades — para que pases cualquier inspección al primer intento. Tu papeleo, tu estudio, tu preparación, todo puede ser en español.":
        "Worried about the ELP rule? <strong>Relax.</strong> Our bilingual instructors teach you the exact English CDL vocabulary — traffic signs, inspections, law-enforcement communication — so you pass any inspection on the first try. Your paperwork, study prep, and training can be in Spanish or English.",
    "Leer: Cambios 2025 en la Industria del Transporte →":
        "Read: 2025 Trucking Industry Changes →",

    # FAQ on-page questions (match schema)
    "Preguntas Frecuentes": "Frequently Asked Questions",
    "PREGUNTAS": "COMMON",
    "COMUNES.": "QUESTIONS.",
    "¿Necesito experiencia previa?": "Do I need prior experience?",
    "No se necesita experiencia. Solo necesitas una licencia de conducir válida, tener 18 años o más, y pasar un examen físico DOT y prueba de drogas. Aceptamos principiantes completos.":
        "No prior experience needed. You just need a valid driver license, be 18 or older, and pass a DOT physical and drug test. Complete beginners welcome.",
    "¿Qué incluye exactamente el precio?": "What does the price include exactly?",
    "Todo. Curso teórico ELDT, cuota del examen CDL, todas las horas de entrenamiento práctico, entrenamiento de inspección pre-viaje y apoyo de colocación laboral. $3,000 fijo, sin costos ocultos.":
        "Everything. ELDT theory course, CDL exam fee, all hands-on training hours, pre-trip inspection training, and job placement support. Flat $3,000 with no hidden costs.",
    "Sí. Trabajamos con socios de financiamiento. Llena el formulario y un asesor se comunicará contigo para hablar de tus opciones — queremos que esto sea accesible para todos los que califiquen.":
        "Yes. We work with financing partners. Fill out the form and an advisor will reach out to discuss your options — we want this to be accessible to every qualified student.",
    "Inscribimos de forma continua por los cupos limitados 1-a-1. Contáctanos hoy para verificar la próxima fecha disponible antes de que se llenen los cupos.":
        "We enroll on a rolling basis because 1-on-1 spots are limited. Contact us today to check the next available start date before spots fill.",
    "Automático vs Manual — ¿cuál debo elegir?": "Automatic vs Manual — which should I pick?",
    "El Automático ($3,000) es más fácil de aprender y perfecto para la mayoría de empleos de camión. El Manual ($3,500) te da un CDL sin restricciones — puedes manejar cualquier camión, lo que significa más opciones de trabajo y mayor paga. Te ayudaremos a elegir durante tu consulta.":
        "Automatic ($3,000) is easier to learn and perfect for most trucking jobs. Manual ($3,500) gives you an unrestricted CDL — you can drive any truck, which means more job options and higher pay. We'll help you decide during your consultation.",
    "ELDT (Entry-Level Driver Training) es el entrenamiento obligatorio que FMCSA exige desde febrero de 2022 para cualquier persona que obtenga un CDL Clase A o B por primera vez. Solo las escuelas registradas en el Training Provider Registry (TPR) de FMCSA pueden certificarte. Nosotros estamos registrados oficialmente — sin ELDT certificado, el DHSMV de Florida no te emite el CDL.":
        "ELDT (Entry-Level Driver Training) is the mandatory training FMCSA has required since February 2022 for anyone getting a Class A or B CDL for the first time. Only schools registered in FMCSA's Training Provider Registry (TPR) can certify you. We are officially registered — without certified ELDT, Florida's DHSMV will not issue your CDL.",
    "No necesitas ser nativo. La regla ELP (vigente desde el 25 de junio de 2025) requiere que puedas comunicarte funcionalmente en inglés con autoridades, leer señales de tránsito, y llenar reportes básicos. Nuestros instructores bilingües te entrenan específicamente en el vocabulario CDL en inglés — señales, inspección, radio — para que pases cualquier inspección sin problema. Tu entrenamiento puede ser en español.":
        "You don't need to be a native speaker. The ELP rule (effective June 25, 2025) requires that you can functionally communicate in English with law enforcement, read traffic signs, and fill out basic reports. Our bilingual instructors train you specifically on the CDL-English vocabulary — signs, inspection, radio — so you pass any inspection without trouble. Your training can be in Spanish or English.",
    "Ver guía completa ELP →": "See full ELP guide →",
    "Licencia de conducir de Florida válida, tarjeta del Seguro Social o ITIN, prueba de residencia en Florida (recibo de utilidad o contrato de renta), examen médico DOT certificado (MCSA-5875 — te ayudamos a agendarlo), y prueba de drogas. Si tienes Permiso de Aprendiz Comercial (CLP) ya — mejor. Si no, te guiamos a sacarlo.":
        "Valid Florida driver license, Social Security card or ITIN, proof of Florida residency (utility bill or lease), certified DOT medical exam (MCSA-5875 — we help you schedule it), and drug test. If you already have a Commercial Learner Permit (CLP) — great. If not, we guide you through getting one.",
    "Datos reales del mercado Tampa 2026: Conductores nuevos OTR ganan $55,000–$65,000 el primer año. Rutas regionales del sureste pagan $1,400–$1,800/semana ($72K–$93K/año). Locales Tampa con experiencia: $65K–$85K. Veteranos 10+ años: $90,873 promedio. Rutas del Puerto de Tampa pagan 20–30% más. Florida no cobra impuesto estatal — te queda más.":
        "Real Tampa market data for 2026: new OTR drivers earn $55,000–$65,000 their first year. Southeast regional routes pay $1,400–$1,800/week ($72K–$93K/year). Experienced Tampa locals: $65K–$85K. 10+ year veterans: $90,873 average. Port of Tampa routes pay 20–30% more. Florida has no state income tax — you keep more.",
    "Ver desglose de salarios →": "See salary breakdown →",
    "Depende de la gravedad y cuánto tiempo haya pasado. Un DUI reciente (menos de 5 años) puede ser descalificante para ciertos empleos; uno antiguo puede no serlo. Felonías violentas y delitos con drogas Schedule I complican HAZMAT. Habla honestamente con un asesor en tu consulta gratuita — revisamos tu caso sin juzgar y te decimos qué puertas siguen abiertas.":
        "It depends on severity and how long ago. A recent DUI (under 5 years) can be disqualifying for certain jobs; an older one may not be. Violent felonies and Schedule I drug offenses complicate HAZMAT. Talk openly with an advisor during your free consultation — we review your case without judgment and tell you which doors are still open.",
    "Un examinador médico certificado (del Registro Nacional FMCSA) revisa: visión (20/40 corregida en ambos ojos), audición (whisper test a 5 pies), presión arterial, diabetes, condiciones cardíacas, historial de epilepsia. Dura 30–45 minutos. Emite la tarjeta MCSA-5875, válida por 2 años (o 1 año si tienes condiciones monitoreadas como hipertensión leve). Te ayudamos a encontrar un examinador aprobado en Tampa.":
        "A certified medical examiner (from FMCSA's National Registry) checks: vision (20/40 corrected both eyes), hearing (whisper test at 5 feet), blood pressure, diabetes, heart conditions, history of epilepsy. Takes 30–45 minutes. Issues the MCSA-5875 card, valid 2 years (or 1 year if you have monitored conditions like mild hypertension). We help you find an approved examiner in Tampa.",
    "¿Dónde se toma el examen CDL?": "Where do I take the CDL exam?",
    "El examen de conocimientos (teórico) se toma en cualquier oficina del FL DHSMV — te ayudamos a agendarlo. El examen de habilidades (inspección pre-viaje + maniobras de patio + manejo en carretera) se toma con un examinador de tercera parte autorizado por el estado. Nosotros programamos todo y te acompañamos. La cuota del examen ya está incluida en tu precio de $3,000.":
        "The knowledge (theory) exam is taken at any FL DHSMV office — we help you schedule it. The skills exam (pre-trip inspection + yard maneuvers + road driving) is given by a state-authorized third-party examiner. We schedule everything and go with you. The exam fee is already included in your $3,000 price.",

    # URGENCY
    "LOS CUPOS SE LLENAN RÁPIDO.": "SPOTS FILL UP FAST.",
    "NO ESPERES.": "DON'T WAIT.",
    "En 4 semanas podrías tener tu CDL y tu primer cheque. La única pregunta es — ¿vas a actuar hoy?":
        "In 4 weeks you could have your CDL and your first paycheck. The only question is — will you take action today?",
    "Reservar Mi Cupo Ahora": "Reserve My Spot Now",
    "Consulta gratis · Sin compromiso · Sin obligación":
        "Free consultation · No obligation · No commitment",

    # FOOTER
    "La escuela CDL bilingüe #1 de Tampa. Instrucción 1-a-1 en español. Desde 2019.":
        "Tampa's #1 bilingual CDL school. 1-on-1 instruction. Since 2019.",
    "Navegación": "Navigation",
    "Inicio": "Home",
    "Programas": "Programs",
    "Salarios": "Salaries",
    "Currículo": "Curriculum",
    "Graduados": "Graduates",
    "Recursos": "Resources",
    "Cómo Obtener CDL en FL": "How to Get a CDL in FL",
    "Regulaciones CDL Florida": "Florida CDL Regulations",
    "Regla ELP 2025": "ELP Rule 2025",
    "Salarios Tampa": "Tampa Salaries",
    "Cambios 2025": "2025 Changes",
    "Contacto": "Contact",
    "Lun–Vie: 8am–6pm": "Mon–Fri: 8am–6pm",
    "Sáb: Con cita previa": "Sat: By appointment",
    "© 2026 CDL Training of Tampa LLC · Negocio Familiar en Tampa, FL":
        "© 2026 CDL Training of Tampa LLC · Family-Owned in Tampa, FL",
    "Inscríbete": "Enroll",
    "Los resultados individuales varían. Los salarios citados reflejan datos de mercado de BLS, Glassdoor, e Indeed (2024–2026) y no constituyen una garantía de ingresos. Colocación laboral sujeta a requisitos del empleador, antecedentes y récord de manejo. CDL Training of Tampa LLC opera como un proveedor de entrenamiento registrado en el FMCSA Training Provider Registry y licenciado por la Comisión para la Educación Independiente de Florida.":
        "Individual results may vary. Cited salaries reflect market data from BLS, Glassdoor, and Indeed (2024–2026) and do not constitute a guarantee of income. Job placement subject to employer requirements, background check, and driving record. CDL Training of Tampa LLC operates as a training provider registered in the FMCSA Training Provider Registry and licensed by the Florida Commission for Independent Education.",
    "Contacto rápido": "Quick contact",

    # Schema FAQPage question names (already in EN dict above via longer strings)
    # Leftover common Spanish words
    "Reservar Mi Cupo": "Reserve My Spot",
    "FMCSA Requirement": "FMCSA Requirement",  # idempotent safety
}

# ============================================================
# PORTUGUESE DICTIONARY
# ============================================================
PT = {
    # Meta + title
    "Escuela CDL en Tampa, FL | Clase A en 4 Semanas | CDL Training of Tampa":
        "Escola CDL em Tampa, FL | Classe A em 4 Semanas | CDL Training of Tampa",
    "Escuela CDL Clase A en Tampa, FL. Certificada FMCSA ELDT. Instrucción 1-a-1 en español. 4 semanas. Desde $3,000 — examen incluido. Colocación laboral real.":
        "Escola CDL Classe A em Tampa, FL. Certificada FMCSA ELDT. Instrução 1-a-1 bilíngue. 4 semanas. A partir de US$ 3.000 — exame incluso. Colocação profissional real.",
    "escuela CDL Tampa, CDL Clase A Florida, ELDT en español, CDL en 4 semanas, camionero Tampa, licencia CDL Florida, entrenamiento camionero, CDL training Tampa":
        "escola CDL Tampa, CDL Classe A Flórida, treinamento ELDT, CDL em 4 semanas, caminhoneiro Tampa, licença CDL Flórida, treinamento motorista caminhão, CDL training Tampa",

    # OG/Twitter
    "Escuela CDL en Tampa, FL | Clase A en 4 Semanas":
        "Escola CDL em Tampa, FL | Classe A em 4 Semanas",
    "Escuela CDL Clase A certificada FMCSA ELDT en Tampa. Instrucción 1-a-1 en español. Desde $3,000 todo incluido. Colocación laboral.":
        "Escola CDL Classe A certificada FMCSA ELDT em Tampa. Instrução 1-a-1 bilíngue. A partir de US$ 3.000 tudo incluído. Colocação profissional.",
    "Escuela CDL certificada FMCSA ELDT en Tampa. Instrucción bilingüe 1-a-1. Desde $3,000. Colocación laboral.":
        "Escola CDL certificada FMCSA ELDT em Tampa. Instrução bilíngue 1-a-1. A partir de US$ 3.000. Colocação profissional.",

    # Schema LocalBusiness description
    "Escuela CDL Clase A aprobada por el estado en Tampa, FL. Entrenamiento ELDT certificado por FMCSA. Instrucción 1-a-1 en español. 4 semanas. Colocación laboral.":
        "Escola CDL Classe A aprovada pelo estado em Tampa, FL. Treinamento ELDT certificado FMCSA. Instrução 1-a-1 bilíngue. 4 semanas. Colocação profissional real.",

    # Schema Course
    "CDL Clase A — Entrenamiento ELDT Completo":
        "CDL Classe A — Treinamento ELDT Completo",
    "Programa de entrenamiento CDL Clase A de 160 horas. Incluye curso teórico ELDT, entrenamiento práctico 1-a-1, examen CDL, y apoyo de colocación laboral. Instructores bilingües.":
        "Programa de treinamento CDL Classe A de 160 horas. Inclui curso teórico ELDT, treinamento prático 1-a-1, exame CDL e apoio na colocação profissional. Instrutores bilíngues.",
    "CDL Clase A — Automático": "CDL Classe A — Automático",
    "CDL Clase A — Manual": "CDL Classe A — Manual",

    # FAQ Schema questions
    "¿Necesito experiencia previa para inscribirme?":
        "Preciso de experiência prévia para me inscrever?",
    "No. Solo necesitas una licencia de conducir válida, tener 18 años o más (21+ para manejar entre estados), pasar un examen físico DOT y una prueba de drogas. Aceptamos principiantes completos.":
        "Não. Você só precisa de carteira de motorista válida, ter 18 anos ou mais (21+ para dirigir entre estados), passar no exame médico DOT e no teste antidrogas. Aceitamos iniciantes completos.",
    "¿Qué incluye exactamente el precio de $3,000?":
        "O que exatamente está incluído no preço de US$ 3.000?",
    "Todo: curso teórico ELDT de 160 horas, cuota del examen CDL, todas las horas de entrenamiento práctico en camión real, inspección pre-viaje, y apoyo de colocación laboral. Sin costos ocultos.":
        "Tudo: curso teórico ELDT de 160 horas, taxa do exame CDL, todas as horas de treinamento prático em caminhão real, inspeção pré-viagem e apoio na colocação profissional. Sem custos ocultos.",
    "¿Ofrecen financiamiento o planes de pago?":
        "Oferecem financiamento ou planos de pagamento?",
    "Sí. Trabajamos con socios de financiamiento. Un asesor revisa tus opciones durante la consulta gratuita.":
        "Sim. Trabalhamos com parceiros de financiamento. Um consultor revisa suas opções durante a consulta gratuita.",
    "¿Cuándo empieza la próxima clase?":
        "Quando começa a próxima turma?",
    "Inscribimos de forma continua debido a los cupos limitados para instrucción 1-a-1. Contacta hoy para verificar la próxima fecha disponible.":
        "Inscrevemos continuamente devido às vagas limitadas para instrução 1-a-1. Entre em contato hoje para verificar a próxima data disponível.",
    "¿Cuál es la diferencia entre Automático y Manual?":
        "Qual é a diferença entre Automático e Manual?",
    "El Automático ($3,000) es más fácil de aprender y cubre la mayoría de empleos. El Manual ($3,500) te da un CDL sin restricciones — puedes manejar cualquier camión, lo que significa más opciones de trabajo y mayor paga.":
        "O Automático (US$ 3.000) é mais fácil de aprender e cobre a maioria dos empregos. O Manual (US$ 3.500) te dá um CDL sem restrições — você pode dirigir qualquer caminhão, o que significa mais opções de trabalho e salário maior.",
    "¿Qué es ELDT y por qué importa?":
        "O que é ELDT e por que importa?",
    "ELDT (Entry-Level Driver Training) es el entrenamiento obligatorio que FMCSA exige desde febrero 2022 para cualquier persona que obtenga un CDL Clase A o B por primera vez. Solo escuelas registradas en el Training Provider Registry (TPR) de FMCSA pueden certificarte. Nosotros estamos registrados.":
        "ELDT (Entry-Level Driver Training) é o treinamento obrigatório que a FMCSA exige desde fevereiro de 2022 para quem obtém um CDL Classe A ou B pela primeira vez. Apenas escolas registradas no Training Provider Registry (TPR) da FMCSA podem certificar você. Nós somos registrados.",
    "¿Necesito hablar inglés perfecto por la regla ELP?":
        "Preciso falar inglês perfeito por causa da regra ELP?",
    "No necesitas ser nativo. La regla ELP (vigente desde junio 2025) requiere que puedas comunicarte funcionalmente en inglés con autoridades, leer señales de tránsito, y llenar reportes básicos. Nuestros instructores bilingües te preparan específicamente para esto.":
        "Você não precisa ser nativo. A regra ELP (em vigor desde junho de 2025) exige que você consiga se comunicar funcionalmente em inglês com as autoridades, ler placas de trânsito e preencher relatórios básicos. Nossos instrutores bilíngues te preparam especificamente para isso.",
    "¿Qué documentos necesito para inscribirme?":
        "Quais documentos preciso para me inscrever?",
    "Licencia de conducir FL válida, tarjeta de seguro social o ITIN, prueba de residencia en Florida, examen médico DOT certificado (MCSA-5875), y prueba de drogas. Te ayudamos con el proceso.":
        "Carteira de motorista da Flórida válida, cartão de Seguro Social ou ITIN, comprovante de residência na Flórida, exame médico DOT certificado (MCSA-5875) e teste antidrogas. Ajudamos você no processo.",
    "¿Cuánto voy a ganar después de graduarme?":
        "Quanto vou ganhar depois de me formar?",
    "Conductores nuevos en Tampa ganan $55,000–$65,000 el primer año (OTR). Rutas regionales del sureste pagan $1,400–$1,800/semana ($72,800–$93,600/año). Conductores locales con experiencia: $65,000–$85,000. Rutas intermodales del Puerto de Tampa pagan 20–30% más.":
        "Motoristas novos em Tampa ganham US$ 55.000–US$ 65.000 no primeiro ano (OTR). Rotas regionais do sudeste pagam US$ 1.400–US$ 1.800/semana (US$ 72.800–US$ 93.600/ano). Motoristas locais experientes: US$ 65.000–US$ 85.000. Rotas intermodais do Porto de Tampa pagam 20–30% mais.",
    "¿Un DUI o récord criminal me descalifica?":
        "Um DUI ou antecedentes criminais me desqualificam?",
    "Depende de la gravedad y cuánto tiempo haya pasado. Un DUI reciente puede ser descalificante; uno antiguo puede no serlo. Habla honestamente con un asesor — revisamos tu caso específico sin juzgar.":
        "Depende da gravidade e do tempo que passou. Um DUI recente pode desqualificar; um antigo pode não desqualificar. Converse honestamente com um consultor — revisamos seu caso específico sem julgamento.",
    "¿Qué pasa en el examen físico DOT?":
        "O que acontece no exame médico DOT?",
    "Un examinador médico certificado revisa visión (20/40 corregida), audición, presión arterial, diabetes, y condiciones cardíacas. Dura 30-45 minutos. Emite tarjeta MCSA-5875 válida por 2 años (o 1 año si tienes condiciones monitoreadas).":
        "Um examinador médico certificado verifica visão (20/40 corrigida), audição, pressão arterial, diabetes e condições cardíacas. Dura 30–45 minutos. Emite o cartão MCSA-5875 válido por 2 anos (ou 1 ano se você tiver condições monitoradas).",

    # Alt tags
    "Instructor bilingüe enseñando inspección pre-viaje a estudiante dentro de cabina de camión Clase A en Tampa":
        "Instrutor bilíngue ensinando inspeção pré-viagem a aluno dentro da cabine de caminhão Classe A em Tampa",
    "Camión Clase A en autopista de Florida al atardecer con palmeras al horizonte":
        "Caminhão Classe A em rodovia da Flórida ao pôr do sol com palmeiras no horizonte",
    "Vista desde cabina de camión Clase A en autopista de Florida de noche con luces y señales":
        "Vista da cabine de caminhão Classe A em rodovia da Flórida à noite com luzes e placas",
    "Licencia CDL Clase A de Florida sobre escritorio con mapa y llaves de camión":
        "Licença CDL Classe A da Flórida sobre mesa com mapa e chaves de caminhão",
    "Chofer hispano en inspección de carretera del Florida Highway Patrol":
        "Motorista hispânico em inspeção de estrada da Florida Highway Patrol",
    "Mapa de Florida con formulario médico DOT y documentos regulatorios CDL":
        "Mapa da Flórida com formulário médico DOT e documentos regulatórios CDL",
    "Instructor explicando inspección pre-viaje a estudiante de CDL":
        "Instrutor explicando inspeção pré-viagem a aluno de CDL",
    "Carlos Alejandro Ortega Garcia — Graduado CDL Training of Tampa":
        "Carlos Alejandro Ortega Garcia — Formado CDL Training of Tampa",
    "Anthony Lewis Friend — Graduado CDL Training of Tampa":
        "Anthony Lewis Friend — Formado CDL Training of Tampa",
    "Alex Antonio Sepulveda Rosado — Graduado CDL Training of Tampa":
        "Alex Antonio Sepulveda Rosado — Formado CDL Training of Tampa",
    "Graduados de CDL Training of Tampa con instructores":
        "Formados da CDL Training of Tampa com instrutores",

    # URGENT BAR + NAV
    "INSCRIPCIONES ABIERTAS — CUPOS LIMITADOS ESTE MES":
        "INSCRIÇÕES ABERTAS — VAGAS LIMITADAS ESTE MÊS",
    "Navegación principal": "Navegação principal",
    "Enlaces principales": "Links principais",
    "Por Qué Nosotros": "Por Que Nós",
    "Seleccionar idioma": "Selecionar idioma",
    "Inscríbete Ahora": "Inscreva-se Agora",

    # HERO
    "Aprobado por el Estado · Certificado FMCSA ELDT":
        "Aprovado pelo Estado · Certificado FMCSA ELDT",
    "Obtén Tu": "Tire Seu",
    "CDL en": "CDL em",
    "4 Semanas.": "4 Semanas.",
    "Gana $1,400–$1,800/Semana en Tampa":
        "Ganhe US$ 1.400–US$ 1.800/Semana em Tampa",
    "La escuela CDL #1 de Tampa desde 2019. Instrucción 1-a-1 en español. Certificada FMCSA ELDT. Examen incluido. Colocación laboral real con empresas que contratan ahora.":
        "A escola CDL nº 1 de Tampa desde 2019. Instrução 1-a-1 bilíngue. Certificada FMCSA ELDT. Exame incluído. Colocação profissional real com empresas contratando agora.",
    "Sin costos ocultos.": "Sem custos ocultos.",
    "47+ Graduados Activos": "47+ Formados Ativos",
    "4.9★ en Google": "4.9★ no Google",
    "Se Habla Español": "Atendimento Bilíngue",
    "Entrenamiento 1-a-1": "Treinamento 1-a-1",
    "Escasez de 80,000 choferes en EE.UU. — demanda récord":
        "Escassez de 80.000 motoristas nos EUA — demanda recorde",
    "Empezar Gratis": "Começar Grátis",

    # LEAD FORM
    "Reserva Tu": "Reserve Sua",
    "Cupo": "Vaga",
    "Consulta gratis.": "Consulta grátis.",
    "Sin compromiso.": "Sem compromisso.",
    "Inscripción mensual": "Inscrição mensal",
    "Solo 5 cupos disponibles": "Apenas 5 vagas disponíveis",
    "Nombre": "Nome",
    "Apellido": "Sobrenome",
    "Teléfono": "Telefone",
    "Correo electrónico": "E-mail",
    "Programa": "Programa",
    "Número de teléfono": "Número de telefone",
    "Selecciona tu programa...": "Selecione seu programa...",
    "CDL Clase A — Automático · $3,000": "CDL Classe A — Automático · US$ 3.000",
    "CDL Clase A — Manual · $3,500": "CDL Classe A — Manual · US$ 3.500",
    "No estoy seguro — necesito más información":
        "Não tenho certeza — preciso de mais informações",
    "Obtener Información Gratis →": "Obter Informações Grátis →",
    "Privado y Seguro · Sin Spam · Nunca Vendido":
        "Privado e Seguro · Sem Spam · Nunca Vendido",
    "Completa todos los campos": "Preencha todos os campos",
    "Enviando...": "Enviando...",
    "✓ ¡Te Llamamos en Menos de 24 Horas!":
        "✓ Ligaremos em Menos de 24 Horas!",
    "Algo salió mal — intenta de nuevo":
        "Algo deu errado — tente novamente",
    "Interés Desconocido": "Interesse Desconhecido",

    # TRUST STRIP
    "Indicadores de confianza": "Indicadores de confiança",
    "Registrado en FMCSA TPR": "Registrado no FMCSA TPR",
    "Licencia Comisión Educación FL": "Licenciado pelo Depto. Educação FL",
    "Instrucción 1-a-1": "Instrução 1-a-1",
    "Colocación Laboral Real": "Colocação Profissional Real",
    "Instructores Bilingües": "Instrutores Bilíngues",
    "Negocio Familiar · Desde 2019": "Empresa Familiar · Desde 2019",

    # PROGRAMS
    "Elige Tu Programa": "Escolha Seu Programa",
    "TODO INCLUIDO.": "TUDO INCLUÍDO.",
    "Sin Costos Ocultos. Jamás.": "Sem Custos Ocultos. Jamais.",
    "Un precio fijo. Examen CDL, curso ELDT, entrenamiento práctico y colocación laboral — todo incluido.":
        "Um preço fixo. Exame CDL, curso ELDT, treinamento prático e colocação profissional — tudo incluído.",
    "Más Popular": "Mais Popular",
    "CDL Clase A": "CDL Classe A",
    "Transmisión Automática · El Camino Más Rápido":
        "Transmissão Automática · O Caminho Mais Rápido",
    " todo incluido": " tudo incluído",
    "Curso ELDT de 160 Horas — Incluido": "Curso ELDT de 160 Horas — Incluído",
    "Examen CDL — Incluido": "Exame CDL — Incluído",
    "Entrenamiento Práctico en Camión Real":
        "Treinamento Prático em Caminhão Real",
    "Entrenamiento de Inspección Pre-Viaje":
        "Treinamento de Inspeção Pré-Viagem",
    "Apoyo de Colocación Laboral": "Apoio na Colocação Profissional",
    "Entrenamiento Lun–Vie Tiempo Completo":
        "Treinamento Seg–Sex Tempo Integral",
    "Inscríbete — $3,000 →": "Inscreva-se — US$ 3.000 →",
    "Inscríbete — $3,500 →": "Inscreva-se — US$ 3.500 →",
    "Máxima Flexibilidad": "Máxima Flexibilidade",
    "Transmisión Manual · Sin Restricciones en la Licencia":
        "Transmissão Manual · Sem Restrições na Licença",
    "Todo lo del Automático, más:": "Tudo do Automático, mais:",
    "Sin Restricción de Transmisión": "Sem Restrição de Transmissão",
    "Maneja Cualquier Camión, En Cualquier Lugar":
        "Dirija Qualquer Caminhão, em Qualquer Lugar",
    "Mayor Potencial de Ingresos": "Maior Potencial de Ganhos",
    "Entrenamiento en Carretera y Patio": "Treinamento em Estrada e Pátio",
    "Máxima Flexibilidad de Carrera": "Máxima Flexibilidade de Carreira",

    # WHY US
    "ESCUELA CDL EN TAMPA": "ESCOLA CDL EM TAMPA",
    "QUE SÍ TE ENSEÑA.": "QUE REALMENTE ENSINA.",
    "No somos una fábrica de graduados. Somos una escuela familiar con instructores bilingües que se aseguran de que pases el examen — y consigas empleo — a la primera.":
        "Não somos uma fábrica de formados. Somos uma escola familiar com instrutores bilíngues que garantem que você passe no exame — e consiga emprego — de primeira.",
    "Sin clases masivas. Un instructor, un estudiante, un camión. Aprendes más rápido y retienes lo que importa para el examen.":
        "Sem turmas lotadas. Um instrutor, um aluno, um caminhão. Você aprende mais rápido e retém o que importa para o exame.",
    "Entrenamiento en español con vocabulario técnico en inglés. Te preparamos para pasar la regla ELP con confianza.":
        "Treinamento bilíngue com vocabulário técnico em inglês. Preparamos você para passar na regra ELP com confiança.",
    "Camiones Reales · Patio Real": "Caminhões Reais · Pátio Real",
    "Entrenas en el mismo tipo de camión que vas a manejar. Patio privado con obstáculos reales para maniobras de examen.":
        "Você treina no mesmo tipo de caminhão que vai dirigir. Pátio privado com obstáculos reais para manobras do exame.",
    "Certificado FMCSA ELDT": "Certificado FMCSA ELDT",
    "Registrados oficialmente en el Training Provider Registry (TPR) de FMCSA. Solo estas escuelas pueden certificarte legalmente para CDL.":
        "Oficialmente registrados no Training Provider Registry (TPR) da FMCSA. Apenas essas escolas podem te certificar legalmente para o CDL.",
    "Licenciado por el Estado de FL": "Licenciado pelo Estado da FL",
    "Licencia oficial de la Comisión para la Educación Independiente de Florida. Cumplimos con todos los estándares del Departamento de Educación.":
        "Licença oficial da Comissão de Educação Independente da Flórida. Cumprimos todos os padrões do Departamento de Educação.",
    "Conexiones directas con transportistas que contratan en Tampa, Florida y el sureste. Te ayudamos a conseguir tu primer empleo antes de graduarte.":
        "Conexões diretas com transportadoras que contratam em Tampa, Flórida e no sudeste. Ajudamos você a conseguir seu primeiro emprego antes de se formar.",

    # SALARIES
    "La Realidad del Salario": "A Realidade do Salário",
    "TU NUEVO SUELDO": "SEU NOVO SALÁRIO",
    "EN 4 SEMANAS.": "EM 4 SEMANAS.",
    "Estos son los números reales del mercado de Tampa en 2026. No promesas vacías — datos verificables de BLS, la industria, y las ofertas actuales de empresas que contratan graduados como los nuestros.":
        "Estes são os números reais do mercado de Tampa em 2026. Sem promessas vazias — dados verificáveis do BLS, da indústria e das ofertas atuais de empresas que contratam formados como os nossos.",
    "Primer Año OTR": "Primeiro Ano OTR",
    "Conductor nuevo, rutas de larga distancia (Over-The-Road).":
        "Motorista novo, rotas de longa distância (Over-The-Road).",
    "Fuente: BLS 2024": "Fonte: BLS 2024",
    "Regional Sureste": "Regional Sudeste",
    "Por semana.": "Por semana.",
    "Rutas regionales Florida–Georgia–Carolinas. Home semanal.":
        "Rotas regionais Flórida–Geórgia–Carolinas. Em casa toda semana.",
    "$72K–$93K/año · Fuente: Glassdoor Tampa":
        "US$ 72K–US$ 93K/ano · Fonte: Glassdoor Tampa",
    "Local Tampa": "Local Tampa",
    "Conductor local con experiencia. En casa todos los días.":
        "Motorista local experiente. Em casa todos os dias.",
    "Fuente: Indeed Tampa": "Fonte: Indeed Tampa",
    "10+ Años Tampa": "10+ Anos em Tampa",
    "Promedio anual para veteranos del volante en Tampa Bay.":
        "Média anual para veteranos do volante em Tampa Bay.",
    "Fuente: Glassdoor 2026": "Fonte: Glassdoor 2026",
    "Ventaja Puerto de Tampa:": "Vantagem do Porto de Tampa:",
    "Los conductores con experiencia intermodal del Puerto de Tampa ganan 20–30% más que el promedio OTR. Tampa es un punto estratégico entre el Puerto de Tampa Bay, JAXPORT y PortMiami — rutas que pocos conductores pueden trabajar.":
        "Motoristas com experiência intermodal no Porto de Tampa ganham 20–30% a mais que a média OTR. Tampa é um ponto estratégico entre o Porto de Tampa Bay, JAXPORT e PortMiami — rotas que poucos motoristas conseguem trabalhar.",
    "Bono Florida:": "Bônus Flórida:",
    "Sin impuestos estatales sobre el ingreso. Cada dólar que ganas rinde más que en otros estados.":
        "Sem imposto estadual sobre a renda. Cada dólar que você ganha rende mais do que em outros estados.",
    "Ver desglose completo de salarios →": "Ver detalhamento completo de salários →",

    # CURRICULUM
    "Lo Que Aprenderás": "O Que Você Vai Aprender",
    "160 HORAS. CERO FILLER.": "160 HORAS. SEM ENROLAÇÃO.",
    "TODO LO QUE EL EXAMEN EXIGE.": "TUDO QUE O EXAME EXIGE.",
    "Nuestro currículo ELDT cubre cada tema que FMCSA requiere, más las habilidades reales que necesitas desde tu primer día en el volante.":
        "Nosso currículo ELDT cobre cada tópico que a FMCSA exige, além das habilidades reais que você precisa desde o primeiro dia no volante.",
    "Teoría FMCSA (30+ Temas)": "Teoria FMCSA (30+ Tópicos)",
    "Regulaciones federales, Horas de Servicio (HOS), ELD, fatiga, manejo defensivo, diario de bitácora, CSA.":
        "Regulamentos federais, Horas de Serviço (HOS), ELD, fadiga, direção defensiva, diário de bordo, CSA.",
    "Inspección Pre-Viaje": "Inspeção Pré-Viagem",
    "Sistema de 3 puntos: motor, sistema de combustible, frenos neumáticos. El punto donde más gente pierde el examen — aquí no.":
        "Sistema de 3 pontos: motor, sistema de combustível, freios pneumáticos. O ponto onde mais gente perde o exame — aqui não.",
    "Maniobras de Patio": "Manobras de Pátio",
    "Parking recto, offset back, alley dock, parallel. Practica en patio privado hasta que sea automático.":
        "Estacionamento reto, offset back, alley dock, paralelo. Prática em pátio privado até ficar automático.",
    "Manejo en Carretera": "Direção em Estrada",
    "Ciudad, autopista, nocturno, lluvia. Rutas reales alrededor de Tampa con tráfico real.":
        "Cidade, rodovia, noturno, chuva. Rotas reais ao redor de Tampa com trânsito real.",
    "Preparación del Examen CDL": "Preparação do Exame CDL",
    "Simulacros completos del examen general, frenos de aire, y combinación. Pasas antes de pisar el DHSMV.":
        "Simulados completos do exame geral, freios de ar e combinação. Você passa antes de pisar no DHSMV.",
    "Regla ELP (Dominio del Inglés)": "Regra ELP (Proficiência em Inglês)",
    "Vocabulario CDL en inglés: señales, inspección, radio, preguntas de tránsito. Cumplimiento garantizado de la regla ELP 2025.":
        "Vocabulário CDL em inglês: placas, inspeção, rádio, perguntas de trânsito. Conformidade garantida com a regra ELP 2025.",
    "Introducción a Endosos": "Introdução aos Endossos",
    "HAZMAT, Tanker, Doubles/Triples, Passenger. Te mostramos cuáles valen la pena para Tampa y cómo prepararte.":
        "HAZMAT, Tanker, Doubles/Triples, Passenger. Mostramos quais valem a pena em Tampa e como se preparar.",
    "Preparación para la Entrevista": "Preparação para Entrevista",
    "Cómo hablar con reclutadores, qué pedir en tu primer contrato, y cómo leer tu carta de empleo (bonos, paga por milla, beneficios).":
        "Como conversar com recrutadores, o que pedir no primeiro contrato e como ler sua carta de emprego (bônus, pagamento por milha, benefícios).",
    "Horas de entrenamiento ELDT certificado · Curso aprobado por FMCSA":
        "Horas de treinamento ELDT certificado · Curso aprovado pela FMCSA",

    # CINEMATIC
    "LA CARRETERA TE": "A ESTRADA TE",
    "ESTÁ ESPERANDO": "ESTÁ ESPERANDO",
    "EN 4 SEMANAS": "EM 4 SEMANAS",
    "ESTA PODRÍA SER TU VISTA.": "ESTA PODERIA SER SUA VISTA.",
    "Camiones en la autopista al atardecer":
        "Caminhões na rodovia ao pôr do sol",
    "Interior de cabina de camión": "Interior da cabine de caminhão",

    # GRADUATES
    "Graduados Reales": "Formados Reais",
    "SUS CARRERAS": "SUAS CARREIRAS",
    "EMPEZARON AQUÍ.": "COMEÇARAM AQUI.",
    "Cada certificado representa una vida transformada. Estos son estudiantes reales de CDL Training of Tampa.":
        "Cada certificado representa uma vida transformada. Estes são alunos reais da CDL Training of Tampa.",
    "Graduado CDL Clase A": "Formado CDL Classe A",
    "Graduado CDL Clase A · Con Nuestros Instructores":
        "Formado CDL Classe A · Com Nossos Instrutores",

    # STEPS
    "El Proceso": "O Processo",
    "DE CERO A CDL": "DO ZERO AO CDL",
    "EN 4 PASOS.": "EM 4 PASSOS.",
    "Envía Tu Información": "Envie Suas Informações",
    "Llena el formulario. Un asesor te contacta en menos de 24 horas para responder preguntas y confirmar disponibilidad.":
        "Preencha o formulário. Um consultor entra em contato em menos de 24 horas para responder dúvidas e confirmar disponibilidade.",
    "Elige Tu Programa": "Escolha Seu Programa",
    "Automático ($3,000) o Manual ($3,500). Te ayudamos a decidir según tus metas profesionales.":
        "Automático (US$ 3.000) ou Manual (US$ 3.500). Ajudamos você a decidir de acordo com seus objetivos de carreira.",
    "Completa el Entrenamiento": "Complete o Treinamento",
    "4 semanas. Lun–Vie. Instrucción 1-a-1 en camiones reales. Instructores bilingües. Examen en sitio cuando estés listo.":
        "4 semanas. Seg–Sex. Instrução 1-a-1 em caminhões reais. Instrutores bilíngues. Exame no local quando você estiver pronto.",
    "Consigue Empleo": "Consiga Emprego",
    "Gradúate con tu CDL en mano. Te conectamos con las mejores empresas de camiones que contratan en Florida.":
        "Forme-se com seu CDL na mão. Conectamos você com as melhores empresas de caminhão contratando na Flórida.",

    # TESTIMONIALS
    "Lo Que Dicen Los Graduados": "O Que Dizem os Formados",
    "RESULTADOS REALES.": "RESULTADOS REAIS.",
    "PERSONAS REALES.": "PESSOAS REAIS.",
    "\"Ganaba $14/hora en un almacén. 4 semanas después de inscribirme ya tenía mi CDL y una oferta de trabajo de $72K. Los instructores son pacientes, profesionales y realmente se preocupan.\"":
        "\"Eu ganhava US$ 14/hora em um armazém. 4 semanas depois de me inscrever, já tinha meu CDL e uma oferta de emprego de US$ 72 mil. Os instrutores são pacientes, profissionais e realmente se importam.\"",
    "Ahora Gana $72K · Conductor OTR": "Agora Ganha US$ 72K · Motorista OTR",
    "\"Pasé el examen de CDL al primer intento gracias a los instructores bilingües. Conseguí trabajo inmediatamente después de graduarme. 100% lo recomiendo a cualquier hispano que quiera un futuro mejor.\"":
        "\"Passei no exame de CDL de primeira graças aos instrutores bilíngues. Consegui emprego logo depois de me formar. Recomendo 100% para qualquer brasileiro que queira um futuro melhor.\"",
    "Graduado CDL · Tampa, FL": "Formado CDL · Tampa, FL",
    "\"La mejor inversión que hice. La instrucción 1-a-1 es diferente a cualquier otra escuela. Aprobé a la primera y tuve 3 ofertas de trabajo en una semana de graduarme.\"":
        "\"O melhor investimento que fiz. A instrução 1-a-1 é diferente de qualquer outra escola. Passei de primeira e recebi 3 ofertas de emprego em uma semana depois de me formar.\"",
    "Graduado Clase A · Contratado": "Formado Classe A · Contratado",

    # BLOG CTA
    "Recursos y Guías": "Recursos e Guias",
    "APRENDE ANTES DE INVERTIR.": "APRENDA ANTES DE INVESTIR.",
    "INFÓRMATE.": "INFORME-SE.",
    "Artículos gratis con información real sobre CDL en Florida: costos, regulaciones, salarios y los cambios 2025 que afectan a todos los conductores hispanos.":
        "Artigos gratuitos com informações reais sobre CDL na Flórida: custos, regulamentos, salários e as mudanças de 2025 que afetam todos os motoristas.",
    "Cómo Obtener Tu CDL en Florida: Guía Paso a Paso 2026":
        "Como Obter Seu CDL na Flórida: Guia Passo a Passo 2026",
    "Todo el proceso explicado: Clase A vs B, ELDT, examen médico DOT, CLP, endosos, y cuánto tarda realmente obtener tu licencia en FL.":
        "Todo o processo explicado: Classe A vs B, ELDT, exame médico DOT, CLP, endossos e quanto tempo leva de fato para obter sua licença na FL.",
    "Leer más →": "Ler mais →",
    "8 min lectura": "8 min leitura",
    "Nuevo 2025": "Novo 2025",
    "Regla ELP: Dominio del Inglés para Choferes CDL (Junio 2025)":
        "Regra ELP: Proficiência em Inglês para Motoristas CDL (Junho 2025)",
    "La nueva regla federal que puede sacarte de servicio al instante. Qué dice, cómo pasas la inspección, y cómo te preparamos para cumplir.":
        "A nova regra federal que pode te tirar de serviço na hora. O que diz, como passar na inspeção e como te preparamos para cumprir.",
    "7 min lectura": "7 min leitura",
    "Regulaciones": "Regulamentos",
    "Regulaciones CDL en Florida: FMCSA, FL DHSMV y Examen Médico DOT":
        "Regulamentos CDL na Flórida: FMCSA, FL DHSMV e Exame Médico DOT",
    "Los requisitos exactos para tu CDL en Florida. Fees reales, tiempos de examen, y qué condiciones médicas pueden descalificarte (y cuáles no).":
        "Os requisitos exatos para seu CDL na Flórida. Taxas reais, prazos de exame e quais condições médicas podem desqualificar você (e quais não).",
    "9 min lectura": "9 min leitura",
    "Ver Todos los Artículos": "Ver Todos os Artigos",
    "Guía": "Guia",

    # 2025 ALERT
    "Alerta · Cambios 2025 en la Industria":
        "Alerta · Mudanças 2025 na Indústria",
    "LA INDUSTRIA CAMBIÓ.": "A INDÚSTRIA MUDOU.",
    "TU OPORTUNIDAD NUNCA FUE MAYOR.": "SUA OPORTUNIDADE NUNCA FOI MAIOR.",
    "Desde el <strong>25 de junio de 2025</strong>, la regla ELP (Dominio del Inglés) está en los Criterios Fuera de Servicio de CVSA. Al mismo tiempo, nuevas reglas federales están sacando a ~200,000 conductores del mercado. <strong>La demanda de choferes certificados nunca fue tan alta.</strong>":
        "Desde <strong>25 de junho de 2025</strong>, a regra ELP (Proficiência em Inglês) está nos Critérios Fora de Serviço da CVSA. Ao mesmo tempo, novas regras federais estão tirando ~200.000 motoristas do mercado. <strong>A demanda por motoristas certificados nunca foi tão alta.</strong>",
    "Escasez de conductores EE.UU. 2025": "Escassez de motoristas EUA 2025",
    "Empleos de camión activos en Tampa ahora":
        "Empregos de caminhão ativos em Tampa agora",
    "Aumento de pago al conductor desde 2016 (ajustado)":
        "Aumento do salário do motorista desde 2016 (ajustado)",
    "¿Hablas español y te preocupa la regla ELP? <strong>Relájate.</strong> Nuestros instructores bilingües te enseñan específicamente el vocabulario CDL en inglés — señales de tránsito, inspecciones, comunicación con autoridades — para que pases cualquier inspección al primer intento. Tu papeleo, tu estudio, tu preparación, todo puede ser en español.":
        "Preocupado com a regra ELP? <strong>Relaxe.</strong> Nossos instrutores bilíngues te ensinam especificamente o vocabulário CDL em inglês — placas de trânsito, inspeções, comunicação com autoridades — para você passar em qualquer inspeção de primeira. Sua papelada, estudo e preparação podem ser em português ou inglês.",
    "Leer: Cambios 2025 en la Industria del Transporte →":
        "Leia: Mudanças 2025 na Indústria de Transporte →",

    # FAQ on-page
    "Preguntas Frecuentes": "Perguntas Frequentes",
    "PREGUNTAS": "PERGUNTAS",
    "COMUNES.": "COMUNS.",
    "¿Necesito experiencia previa?": "Preciso de experiência prévia?",
    "No se necesita experiencia. Solo necesitas una licencia de conducir válida, tener 18 años o más, y pasar un examen físico DOT y prueba de drogas. Aceptamos principiantes completos.":
        "Não precisa de experiência. Você só precisa de carteira de motorista válida, ter 18 anos ou mais e passar no exame médico DOT e no teste antidrogas. Aceitamos iniciantes completos.",
    "¿Qué incluye exactamente el precio?": "O que exatamente o preço inclui?",
    "Todo. Curso teórico ELDT, cuota del examen CDL, todas las horas de entrenamiento práctico, entrenamiento de inspección pre-viaje y apoyo de colocación laboral. $3,000 fijo, sin costos ocultos.":
        "Tudo. Curso teórico ELDT, taxa do exame CDL, todas as horas de treinamento prático, treinamento de inspeção pré-viagem e apoio na colocação profissional. US$ 3.000 fixos, sem custos ocultos.",
    "Sí. Trabajamos con socios de financiamiento. Llena el formulario y un asesor se comunicará contigo para hablar de tus opciones — queremos que esto sea accesible para todos los que califiquen.":
        "Sim. Trabalhamos com parceiros de financiamento. Preencha o formulário e um consultor entrará em contato para falar sobre suas opções — queremos que isso seja acessível para todos que se qualificarem.",
    "Inscribimos de forma continua por los cupos limitados 1-a-1. Contáctanos hoy para verificar la próxima fecha disponible antes de que se llenen los cupos.":
        "Inscrevemos continuamente por causa das vagas limitadas para 1-a-1. Entre em contato hoje para verificar a próxima data disponível antes que as vagas se esgotem.",
    "Automático vs Manual — ¿cuál debo elegir?":
        "Automático vs Manual — qual devo escolher?",
    "El Automático ($3,000) es más fácil de aprender y perfecto para la mayoría de empleos de camión. El Manual ($3,500) te da un CDL sin restricciones — puedes manejar cualquier camión, lo que significa más opciones de trabajo y mayor paga. Te ayudaremos a elegir durante tu consulta.":
        "O Automático (US$ 3.000) é mais fácil de aprender e perfeito para a maioria dos empregos. O Manual (US$ 3.500) te dá um CDL sem restrições — você pode dirigir qualquer caminhão, o que significa mais opções de trabalho e salário maior. Ajudaremos você a escolher durante a consulta.",
    "ELDT (Entry-Level Driver Training) es el entrenamiento obligatorio que FMCSA exige desde febrero de 2022 para cualquier persona que obtenga un CDL Clase A o B por primera vez. Solo las escuelas registradas en el Training Provider Registry (TPR) de FMCSA pueden certificarte. Nosotros estamos registrados oficialmente — sin ELDT certificado, el DHSMV de Florida no te emite el CDL.":
        "ELDT (Entry-Level Driver Training) é o treinamento obrigatório que a FMCSA exige desde fevereiro de 2022 para quem obtém um CDL Classe A ou B pela primeira vez. Apenas escolas registradas no Training Provider Registry (TPR) da FMCSA podem te certificar. Somos oficialmente registrados — sem ELDT certificado, o DHSMV da Flórida não emite seu CDL.",
    "No necesitas ser nativo. La regla ELP (vigente desde el 25 de junio de 2025) requiere que puedas comunicarte funcionalmente en inglés con autoridades, leer señales de tránsito, y llenar reportes básicos. Nuestros instructores bilingües te entrenan específicamente en el vocabulario CDL en inglés — señales, inspección, radio — para que pases cualquier inspección sin problema. Tu entrenamiento puede ser en español.":
        "Você não precisa ser nativo. A regra ELP (em vigor desde 25 de junho de 2025) exige que você se comunique funcionalmente em inglês com as autoridades, leia placas de trânsito e preencha relatórios básicos. Nossos instrutores bilíngues te treinam especificamente no vocabulário CDL em inglês — placas, inspeção, rádio — para que você passe em qualquer inspeção sem problemas. Seu treinamento pode ser em português.",
    "Ver guía completa ELP →": "Ver guia completo ELP →",
    "Licencia de conducir de Florida válida, tarjeta del Seguro Social o ITIN, prueba de residencia en Florida (recibo de utilidad o contrato de renta), examen médico DOT certificado (MCSA-5875 — te ayudamos a agendarlo), y prueba de drogas. Si tienes Permiso de Aprendiz Comercial (CLP) ya — mejor. Si no, te guiamos a sacarlo.":
        "Carteira de motorista da Flórida válida, cartão do Seguro Social ou ITIN, comprovante de residência na Flórida (conta de luz ou contrato de aluguel), exame médico DOT certificado (MCSA-5875 — te ajudamos a agendar) e teste antidrogas. Se você já tiver Permissão de Aprendiz Comercial (CLP) — melhor. Se não, te guiamos para obter.",
    "Datos reales del mercado Tampa 2026: Conductores nuevos OTR ganan $55,000–$65,000 el primer año. Rutas regionales del sureste pagan $1,400–$1,800/semana ($72K–$93K/año). Locales Tampa con experiencia: $65K–$85K. Veteranos 10+ años: $90,873 promedio. Rutas del Puerto de Tampa pagan 20–30% más. Florida no cobra impuesto estatal — te queda más.":
        "Dados reais do mercado de Tampa 2026: motoristas novos OTR ganham US$ 55.000–US$ 65.000 no primeiro ano. Rotas regionais do sudeste pagam US$ 1.400–US$ 1.800/semana (US$ 72K–US$ 93K/ano). Locais de Tampa experientes: US$ 65K–US$ 85K. Veteranos 10+ anos: US$ 90.873 em média. Rotas do Porto de Tampa pagam 20–30% mais. A Flórida não cobra imposto estadual — você fica com mais.",
    "Ver desglose de salarios →": "Ver detalhamento de salários →",
    "Depende de la gravedad y cuánto tiempo haya pasado. Un DUI reciente (menos de 5 años) puede ser descalificante para ciertos empleos; uno antiguo puede no serlo. Felonías violentas y delitos con drogas Schedule I complican HAZMAT. Habla honestamente con un asesor en tu consulta gratuita — revisamos tu caso sin juzgar y te decimos qué puertas siguen abiertas.":
        "Depende da gravidade e do tempo que passou. Um DUI recente (menos de 5 anos) pode desqualificar para certos empregos; um antigo pode não desqualificar. Crimes violentos e delitos de drogas Schedule I complicam HAZMAT. Converse honestamente com um consultor na consulta gratuita — revisamos seu caso sem julgamento e dizemos quais portas continuam abertas.",
    "Un examinador médico certificado (del Registro Nacional FMCSA) revisa: visión (20/40 corregida en ambos ojos), audición (whisper test a 5 pies), presión arterial, diabetes, condiciones cardíacas, historial de epilepsia. Dura 30–45 minutos. Emite la tarjeta MCSA-5875, válida por 2 años (o 1 año si tienes condiciones monitoreadas como hipertensión leve). Te ayudamos a encontrar un examinador aprobado en Tampa.":
        "Um examinador médico certificado (do Registro Nacional FMCSA) verifica: visão (20/40 corrigida em ambos os olhos), audição (whisper test a 5 pés), pressão arterial, diabetes, condições cardíacas, histórico de epilepsia. Dura 30–45 minutos. Emite o cartão MCSA-5875, válido por 2 anos (ou 1 ano se você tiver condições monitoradas como hipertensão leve). Ajudamos você a encontrar um examinador aprovado em Tampa.",
    "¿Dónde se toma el examen CDL?": "Onde se faz o exame CDL?",
    "El examen de conocimientos (teórico) se toma en cualquier oficina del FL DHSMV — te ayudamos a agendarlo. El examen de habilidades (inspección pre-viaje + maniobras de patio + manejo en carretera) se toma con un examinador de tercera parte autorizado por el estado. Nosotros programamos todo y te acompañamos. La cuota del examen ya está incluida en tu precio de $3,000.":
        "O exame de conhecimentos (teórico) é feito em qualquer escritório do FL DHSMV — ajudamos a agendar. O exame de habilidades (inspeção pré-viagem + manobras de pátio + direção em estrada) é feito com um examinador terceirizado autorizado pelo estado. Programamos tudo e acompanhamos você. A taxa do exame já está incluída no seu preço de US$ 3.000.",

    # URGENCY
    "LOS CUPOS SE LLENAN RÁPIDO.": "AS VAGAS ESGOTAM RÁPIDO.",
    "NO ESPERES.": "NÃO ESPERE.",
    "En 4 semanas podrías tener tu CDL y tu primer cheque. La única pregunta es — ¿vas a actuar hoy?":
        "Em 4 semanas você poderia ter seu CDL e seu primeiro cheque. A única pergunta é — você vai agir hoje?",
    "Reservar Mi Cupo Ahora": "Reservar Minha Vaga Agora",
    "Consulta gratis · Sin compromiso · Sin obligación":
        "Consulta grátis · Sem compromisso · Sem obrigação",

    # FOOTER
    "La escuela CDL bilingüe #1 de Tampa. Instrucción 1-a-1 en español. Desde 2019.":
        "A escola CDL bilíngue nº 1 de Tampa. Instrução 1-a-1. Desde 2019.",
    "Navegación": "Navegação",
    "Inicio": "Início",
    "Programas": "Programas",
    "Salarios": "Salários",
    "Currículo": "Currículo",
    "Graduados": "Formados",
    "Recursos": "Recursos",
    "Cómo Obtener CDL en FL": "Como Obter CDL na FL",
    "Regulaciones CDL Florida": "Regulamentos CDL Flórida",
    "Regla ELP 2025": "Regra ELP 2025",
    "Salarios Tampa": "Salários Tampa",
    "Cambios 2025": "Mudanças 2025",
    "Contacto": "Contato",
    "Lun–Vie: 8am–6pm": "Seg–Sex: 8h–18h",
    "Sáb: Con cita previa": "Sáb: Com agendamento",
    "© 2026 CDL Training of Tampa LLC · Negocio Familiar en Tampa, FL":
        "© 2026 CDL Training of Tampa LLC · Empresa Familiar em Tampa, FL",
    "Inscríbete": "Inscreva-se",
    "Los resultados individuales varían. Los salarios citados reflejan datos de mercado de BLS, Glassdoor, e Indeed (2024–2026) y no constituyen una garantía de ingresos. Colocación laboral sujeta a requisitos del empleador, antecedentes y récord de manejo. CDL Training of Tampa LLC opera como un proveedor de entrenamiento registrado en el FMCSA Training Provider Registry y licenciado por la Comisión para la Educación Independiente de Florida.":
        "Os resultados individuais variam. Os salários citados refletem dados de mercado do BLS, Glassdoor e Indeed (2024–2026) e não constituem garantia de renda. Colocação profissional sujeita aos requisitos do empregador, antecedentes e registro de direção. A CDL Training of Tampa LLC opera como provedora de treinamento registrada no FMCSA Training Provider Registry e licenciada pela Comissão de Educação Independente da Flórida.",
    "Contacto rápido": "Contato rápido",
}


def translate(source: str, dictionary: dict) -> str:
    """Apply translations longest-first to avoid partial-match collisions."""
    out = source
    for key in sorted(dictionary.keys(), key=len, reverse=True):
        out = out.replace(key, dictionary[key])
    return out


def apply_en_url_fixes(html: str) -> str:
    """Update lang, canonical, hreflang, OG, schema URLs for English."""
    html = re.sub(r'<html lang="es">', '<html lang="en">', html, count=1)
    html = html.replace('"es_US"', '"en_US"')
    html = html.replace('"es-US"', '"en-US"')
    html = re.sub(
        r'<link rel="canonical" href="https://es\.cdltraintampa\.com/"/>',
        '<link rel="canonical" href="https://en.cdltraintampa.com/"/>',
        html,
    )
    # hreflang: self must be EN, alternate ES + PT
    html = html.replace(
        '<link rel="alternate" hreflang="es" href="https://es.cdltraintampa.com/"/>',
        '<link rel="alternate" hreflang="en" href="https://en.cdltraintampa.com/"/>\n'
        '  <link rel="alternate" hreflang="es" href="https://es.cdltraintampa.com/"/>\n'
        '  <link rel="alternate" hreflang="pt" href="https://pt.cdltraintampa.com/"/>',
    )
    # Remove the pre-existing en alternate + x-default (we'll re-add x-default)
    html = html.replace(
        '<link rel="alternate" hreflang="en" href="https://cdltraintampa.com/"/>\n',
        '',
    )
    html = html.replace(
        '<link rel="alternate" hreflang="x-default" href="https://cdltraintampa.com/"/>',
        '<link rel="alternate" hreflang="x-default" href="https://en.cdltraintampa.com/"/>',
    )
    # Canonical domain in OG and schema
    html = html.replace('https://es.cdltraintampa.com', 'https://en.cdltraintampa.com')
    # inLanguage in schema
    html = html.replace('"inLanguage":["es","en"]', '"inLanguage":["en","es","pt"]')
    html = html.replace('"inLanguage":"es"', '"inLanguage":"en"')
    # Footer "English" link: should point to ES site
    html = html.replace(
        '<a href="https://cdltraintampa.com/" rel="alternate" hreflang="en">English</a>',
        '<a href="https://es.cdltraintampa.com/" rel="alternate" hreflang="es">Español</a>',
    )
    return html


def apply_pt_url_fixes(html: str) -> str:
    """Update lang, canonical, hreflang, OG, schema URLs for Portuguese."""
    html = re.sub(r'<html lang="es">', '<html lang="pt-BR">', html, count=1)
    html = html.replace('"es_US"', '"pt_BR"')
    html = html.replace('"es-US"', '"pt-BR"')
    html = re.sub(
        r'<link rel="canonical" href="https://es\.cdltraintampa\.com/"/>',
        '<link rel="canonical" href="https://pt.cdltraintampa.com/"/>',
        html,
    )
    html = html.replace(
        '<link rel="alternate" hreflang="es" href="https://es.cdltraintampa.com/"/>',
        '<link rel="alternate" hreflang="pt" href="https://pt.cdltraintampa.com/"/>\n'
        '  <link rel="alternate" hreflang="es" href="https://es.cdltraintampa.com/"/>\n'
        '  <link rel="alternate" hreflang="en" href="https://en.cdltraintampa.com/"/>',
    )
    html = html.replace(
        '<link rel="alternate" hreflang="en" href="https://cdltraintampa.com/"/>\n',
        '',
    )
    html = html.replace(
        '<link rel="alternate" hreflang="x-default" href="https://cdltraintampa.com/"/>',
        '<link rel="alternate" hreflang="x-default" href="https://en.cdltraintampa.com/"/>',
    )
    html = html.replace('https://es.cdltraintampa.com', 'https://pt.cdltraintampa.com')
    html = html.replace('"inLanguage":["es","en"]', '"inLanguage":["pt","es","en"]')
    html = html.replace('"inLanguage":"es"', '"inLanguage":"pt-BR"')
    # Footer language alternate link
    html = html.replace(
        '<a href="https://cdltraintampa.com/" rel="alternate" hreflang="en">English</a>',
        '<a href="https://es.cdltraintampa.com/" rel="alternate" hreflang="es">Español</a>',
    )
    return html


def remove_blog_links(html: str) -> str:
    """Remove or redirect blog section since EN/PT sites don't host blog."""
    # Replace internal blog anchor in Blog CTA section with ES blog URLs
    # (users clicking through will trigger translate.js cookie sync)
    html = html.replace(
        'href="/blog/"',
        'href="https://es.cdltraintampa.com/blog/"',
    )
    html = html.replace(
        'href="/blog/como-obtener-cdl-florida/"',
        'href="https://es.cdltraintampa.com/blog/como-obtener-cdl-florida/"',
    )
    html = html.replace(
        'href="/blog/dominio-ingles-cdl/"',
        'href="https://es.cdltraintampa.com/blog/dominio-ingles-cdl/"',
    )
    html = html.replace(
        'href="/blog/regulaciones-cdl-florida/"',
        'href="https://es.cdltraintampa.com/blog/regulaciones-cdl-florida/"',
    )
    html = html.replace(
        'href="/blog/cambios-industria-2025/"',
        'href="https://es.cdltraintampa.com/blog/cambios-industria-2025/"',
    )
    html = html.replace(
        'href="/blog/salario-camionero-tampa/"',
        'href="https://es.cdltraintampa.com/blog/salario-camionero-tampa/"',
    )
    return html


def main():
    src = SRC.read_text()

    # English
    en = translate(src, EN)
    en = apply_en_url_fixes(en)
    en = remove_blog_links(en)
    EN_DST.write_text(en)
    print(f"[EN] wrote {EN_DST} ({len(en)} chars)")

    # Portuguese
    pt = translate(src, PT)
    pt = apply_pt_url_fixes(pt)
    pt = remove_blog_links(pt)
    PT_DST.write_text(pt)
    print(f"[PT] wrote {PT_DST} ({len(pt)} chars)")


if __name__ == "__main__":
    main()
