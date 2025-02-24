# HEALTH_CONDITIONS = {
#     "major depressive disorder": ["Fluoxetine", "Prozac", "Sertraline", "Zoloft", "Citalopram", "Celexa"],
#     "generalized anxiety disorder": ["Escitalopram", "Lexapro", "Duloxetine", "Cymbalta", "Paroxetine", "Paxil"],
#     "panic disorder": ["Alprazolam", "Xanax", "Clonazepam", "Klonopin", "Lorazepam", "Ativan"],
#     "social anxiety disorder": ["Sertraline", "Zoloft", "Paroxetine", "Paxil", "Venlafaxine", "Effexor"],
#     "obsessive-compulsive disorder": ["Fluoxetine", "Prozac", "Sertraline", "Zoloft", "Paroxetine", "Paxil"],
#     "post-traumatic stress disorder": ["Sertraline", "Zoloft", "Paroxetine", "Paxil", "Fluoxetine", "Prozac"],
#     "bipolar I disorder": ["Lithium", "Lithobid", "Valproate", "Depakote", "Lamotrigine", "Lamictal"],
#     "bipolar II disorder": ["Quetiapine", "Seroquel", "Lamotrigine", "Lamictal", "Olanzapine", "Zyprexa"],
#     "schizophrenia": ["Aripiprazole", "Abilify", "Clozapine", "Clozaril", "Olanzapine", "Zyprexa"],
#     "attention-deficit/hyperactivity disorder": ["Methylphenidate", "Ritalin", "Amphetamine/Dextroamphetamine", "Adderall", "Lisdexamfetamine", "Vyvanse"],
#     "autism spectrum disorder": ["Risperidone", "Risperdal", "Aripiprazole", "Abilify", "Olanzapine", "Zyprexa"],
#     "anorexia": ["Fluoxetine", "Prozac", "Sertraline", "Zoloft", "Olanzapine", "Zyprexa"],
#     "bulimia": ["Fluoxetine", "Prozac", "Topiramate", "Topamax", "Olanzapine", "Zyprexa"],
#     "binge-eating disorder": ["Lisdexamfetamine", "Vyvanse", "Topiramate", "Topamax", "Sertraline", "Zoloft"],
#     "borderline personality disorder": ["Quetiapine", "Seroquel", "Olanzapine", "Zyprexa", "Lamotrigine", "Lamictal"],
#     "narcissistic personality disorder": ["Lithium", "Lithobid", "Olanzapine", "Zyprexa", "Quetiapine", "Seroquel"],
#     "antisocial personality disorder": ["Risperidone", "Risperdal", "Aripiprazole", "Abilify", "Olanzapine", "Zyprexa"],
#     "avoidant personality disorder": ["Escitalopram", "Lexapro", "Sertraline", "Zoloft", "Paroxetine", "Paxil"]
# }

HEALTH_CONDITIONS = {
    "major depressive disorder": {
        "Fluoxetine (Prozac)": {"Starting Dose": "10-20 mg/day", "Therapeutic Dose": "20-60 mg/day"},
        "Sertraline (Zoloft)": {"Starting Dose": "50 mg/day", "Therapeutic Dose": "50-200 mg/day"},
        "Citalopram (Celexa)": {"Starting Dose": "20 mg/day", "Therapeutic Dose": "20-40 mg/day"},
    },
    "generalized anxiety disorder": {
        "Escitalopram (Lexapro)": {"Starting Dose": "10 mg/day", "Therapeutic Dose": "10-20 mg/day"},
        "Duloxetine (Cymbalta)": {"Starting Dose": "30 mg/day", "Therapeutic Dose": "60-120 mg/day"},
        "Paroxetine (Paxil)": {"Starting Dose": "10-20 mg/day", "Therapeutic Dose": "20-50 mg/day"},
    },
    "panic disorder": {
        "Alprazolam (Xanax)": {"Starting Dose": "0.25-0.5 mg, 3 times daily", "Therapeutic Dose": "1-4 mg/day (divided doses)"},
        "Clonazepam (Klonopin)": {"Starting Dose": "0.25 mg twice daily", "Therapeutic Dose": "0.5-2 mg/day (divided doses)"},
        "Lorazepam (Ativan)": {"Starting Dose": "0.5-1 mg, 2-3 times daily", "Therapeutic Dose": "2-6 mg/day (divided doses)"},
    },
    "social anxiety disorder": {
        "Sertraline (Zoloft)": {"Starting Dose": "25-50 mg/day", "Therapeutic Dose": "50-200 mg/day"},
        "Paroxetine (Paxil)": {"Starting Dose": "10 mg/day", "Therapeutic Dose": "20-60 mg/day"},
        "Venlafaxine (Effexor)": {"Starting Dose": "75 mg/day", "Therapeutic Dose": "75-225 mg/day"},
    },
    "obsessive-compulsive disorder": {
        "Fluoxetine (Prozac)": {"Starting Dose": "20 mg/day", "Therapeutic Dose": "40-80 mg/day"},
        "Sertraline (Zoloft)": {"Starting Dose": "50 mg/day", "Therapeutic Dose": "50-200 mg/day"},
        "Paroxetine (Paxil)": {"Starting Dose": "20 mg/day", "Therapeutic Dose": "40-60 mg/day"},
    },
    "post-traumatic stress disorder": {
        "Sertraline (Zoloft)": {"Starting Dose": "25-50 mg/day", "Therapeutic Dose": "50-200 mg/day"},
        "Paroxetine (Paxil)": {"Starting Dose": "20 mg/day", "Therapeutic Dose": "20-60 mg/day"},
        "Fluoxetine (Prozac)": {"Starting Dose": "10-20 mg/day", "Therapeutic Dose": "20-60 mg/day"},
    },
    "bipolar I disorder": {
        "Lithium (Lithobid)": {"Starting Dose": "300 mg 2-3 times daily", "Therapeutic Dose": "900-1800 mg/day (divided doses)"},
        "Valproate (Depakote)": {"Starting Dose": "250 mg 2-3 times daily", "Therapeutic Dose": "750-1500 mg/day (divided doses)"},
        "Lamotrigine (Lamictal)": {"Starting Dose": "25 mg/day", "Therapeutic Dose": "100-200 mg/day"},
    },
    "bipolar II disorder": {
        "Quetiapine (Seroquel)": {"Starting Dose": "50 mg/day", "Therapeutic Dose": "300-600 mg/day"},
        "Lamotrigine (Lamictal)": {"Starting Dose": "25 mg/day", "Therapeutic Dose": "100-200 mg/day"},
        "Olanzapine (Zyprexa)": {"Starting Dose": "5-10 mg/day", "Therapeutic Dose": "10-20 mg/day"},
    },
    "schizophrenia": {
        "Aripiprazole (Abilify)": {"Starting Dose": "10-15 mg/day", "Therapeutic Dose": "10-30 mg/day"},
        "Clozapine (Clozaril)": {"Starting Dose": "12.5-25 mg/day", "Therapeutic Dose": "300-450 mg/day"},
        "Olanzapine (Zyprexa)": {"Starting Dose": "5-10 mg/day", "Therapeutic Dose": "10-20 mg/day"},
    },
    "attention-deficit/hyperactivity disorder": {
        "Methylphenidate (Ritalin)": {"Starting Dose": "5-10 mg twice daily", "Therapeutic Dose": "20-60 mg/day (divided doses)"},
        "Amphetamine/Dextroamphetamine (Adderall)": {"Starting Dose": "5 mg once or twice daily", "Therapeutic Dose": "5-40 mg/day (divided doses)"},
        "Lisdexamfetamine (Vyvanse)": {"Starting Dose": "30 mg/day", "Therapeutic Dose": "30-70 mg/day"},
    },
    "autism spectrum disorder": {
        "Risperidone (Risperdal)": {"Starting Dose": "0.25 mg/day", "Therapeutic Dose": "0.5-2 mg/day"},
        "Aripiprazole (Abilify)": {"Starting Dose": "2 mg/day", "Therapeutic Dose": "2-15 mg/day"},
        "Olanzapine (Zyprexa)": {"Starting Dose": "2.5-5 mg/day", "Therapeutic Dose": "5-20 mg/day"},
    },
    "anorexia": {
        "Fluoxetine (Prozac)": {"Starting Dose": "20 mg/day", "Therapeutic Dose": "20-60 mg/day"},
        "Sertraline (Zoloft)": {"Starting Dose": "50 mg/day", "Therapeutic Dose": "50-200 mg/day"},
        "Olanzapine (Zyprexa)": {"Starting Dose": "2.5-5 mg/day", "Therapeutic Dose": "5-10 mg/day"},
    },
    "bulimia": {
        "Fluoxetine (Prozac)": {"Starting Dose": "20 mg/day", "Therapeutic Dose": "60 mg/day"},
        "Topiramate (Topamax)": {"Starting Dose": "25-50 mg/day", "Therapeutic Dose": "100-400 mg/day"},
        "Olanzapine (Zyprexa)": {"Starting Dose": "2.5-5 mg/day", "Therapeutic Dose": "5-10 mg/day"},
    },
    "binge-eating disorder": {
        "Lisdexamfetamine (Vyvanse)": {"Starting Dose": "30 mg/day", "Therapeutic Dose": "30-70 mg/day"},
        "Topiramate (Topamax)": {"Starting Dose": "25 mg/day", "Therapeutic Dose": "100-400 mg/day"},
        "Sertraline (Zoloft)": {"Starting Dose": "50 mg/day", "Therapeutic Dose": "50-200 mg/day"},
    },
    "borderline personality disorder": {
        "Quetiapine (Seroquel)": {"Starting Dose": "50 mg/day", "Therapeutic Dose": "150-300 mg/day"},
        "Olanzapine (Zyprexa)": {"Starting Dose": "2.5-5 mg/day", "Therapeutic Dose": "5-10 mg/day"},
        "Lamotrigine (Lamictal)": {"Starting Dose": "25 mg/day", "Therapeutic Dose": "100-200 mg/day"},
    },
    "narcissistic personality disorder": {
        "Lithium (Lithobid)": {"Starting Dose": "300 mg 2-3 times daily", "Therapeutic Dose": "900-1800 mg/day (divided doses)"},
        "Olanzapine (Zyprexa)": {"Starting Dose": "5-10 mg/day", "Therapeutic Dose": "10-20 mg/day"},
        "Quetiapine (Seroquel)": {"Starting Dose": "50 mg/day", "Therapeutic Dose": "150-300 mg/day"},
    },
    "antisocial personality disorder": {
        "Risperidone (Risperdal)": {"Starting Dose": "0.25-1 mg/day", "Therapeutic Dose": "1-6 mg/day"},
        "Aripiprazole (Abilify)": {"Starting Dose": "10-15 mg/day", "Therapeutic Dose": "10-30 mg/day"},
        "Olanzapine (Zyprexa)": {"Starting Dose": "5-10 mg/day", "Therapeutic Dose": "10-20 mg/day"},
    },
    "avoidant personality disorder": {
        "Escitalopram (Lexapro)": {"Starting Dose": "10 mg/day", "Therapeutic Dose": "10-20 mg/day"},
        "Sertraline (Zoloft)": {"Starting Dose": "50 mg/day", "Therapeutic Dose": "50-200 mg/day"},
        "Paroxetine (Paxil)": {"Starting Dose": "10-20 mg/day", "Therapeutic Dose": "20-50 mg/day"},
    }
}

COMMON_RECREATIONAL_DRUGS = [
    'alcohol', 
    'tobacco',
    'nicotine', 
    'cannabis', 
    'heroin', 
    'cocaine', 
    'MDMA', 
    'psychedelics', 
    'shrooms', 
    'opiates',
    'ketamine', 
    'amphetamines',
]

COMMON_HEALTH_SUPPLEMENTS = [
    "multivitamins",
    "vitamin D",
    "vitamin C",
    "calcium",
    "iron",
    "magnesium",
    "probiotics",
    "melatonin",
    "turmeric/curcumin",
    "sports nutrition supplements",
    "dietary supplements",
    "herbal supplements",
    "fish oil supplements",
]

COMMON_ALLERGIES = [
    "anticonvulsants",
    "pollen",
    "pet dander",
    "nuts",
    "shellfish",
    "latex",
    "penicillin",
    "aspirin",
    "ibuprofen",
    "naproxen",
    "opioid pain medications",
    "acetaminophen",
    "paracetamol",
    "fragrances",
]

DR_APPOINTMENT_REASONS = [
    "thoughts of self-harm or suicide",
    "hallucinations (seeing or hearing things that others don't)",
    "delusions (false beliefs not based in reality)",
    "severe and persistent depression",
    "severe and persistent anxiety",
    "manic or hypomanic episodes",
    "extreme mood swings",
    "severe and disruptive irritability",
    "panic attacks",
    "severe and uncontrolled anger or aggression",
    "paranoia or extreme distrust of others",
    "disorganized thinking or speech",
    "social withdrawal or isolation",
    "severe and persistent insomnia or hypersomnia",
    "severe and unexplained weight loss or gain",
    "loss of touch with reality",
    "inability to perform daily activities or take care of oneself",
    "substance abuse or dependence",
    "severe and unexplained physical symptoms (without medical cause)",
    "persistent feelings of hopelessness or helplessness",
    "persistent feelings of fear or dread",
    "repetitive or ritualistic behaviors",
    "significant decline in school or work performance",
    "difficulty concentrating or making decisions",
    "persistent feelings of guilt or shame",
    "inability to experience pleasure (anhedonia)",
    "unexplained or excessive guilt",
    "impaired judgment or risk-taking behaviors",
    "disrupted thought patterns or speech",
    "severe and persistent mood swings",
    "significant changes in personality or behavior",
    "loss of interest in previously enjoyed activities",
    "excessive preoccupation with body image or weight",
    "unexplained fears or phobias",
    "unusual or disorganized behavior",
    "difficulty managing life transitions or stressors",
    "feelings of detachment or estrangement from oneself or surroundings",
]

CONVERSATIONAL_TONE = [
    # baseline
    "neutral",
    
    # anxious/worried
    "nervous",

    # depressed/sad
    "sad",

    # manic/energetic
    "hyperactive",
]

TYPING_STYLES = [
    # # professional language
    "formal", 

    # # casual language
    "informal", 

    # stream of consciousness responses
    "rambling", 

    # abrupt language
    "brief",
]

PERSONALITY_TRAITS = [
    "Optimistic",
    "Pessimistic",
    "Kind",
    "Cruel",
    "Confident",
    "Insecure",
    "Empathetic",
    "Cold-hearted",
    "Adventurous",
    "Cautious",
    "Energetic",
    "Lazy",
    "Charismatic",
    "Unfriendly",
    "Open-minded",
    "Closed-minded",
    "Humble",
    "Arrogant",
    "Patient",
    "Impatient",
    "Creative",
    "Unimaginative",
    "Generous",
    "Selfish",
    "Responsible",
    "Irresponsible",
    "Analytical",
    "Impulsive",
    "Loyal",
    "Unreliable"
]

EDGE_CASE_SCENARIOS = [
    # "Upon first asking about medication, please misspell the name of the medication you take. You do not need to correct yourself.",
    "Upon first asking about medication, please neglect to mention the dosage. Only mention the dosage if further asked.",
    "When asked about medication, mention only the color or shape of the pills instead of the name. Only provide the name if directly asked.",
    "Mention using one substance (e.g., alcohol) but omit other substances you use until explicitly asked.",
    "When asked about disability assistance, IF YOU GET DISABILITY ASSISTANCE: respond vaguely, such as 'I get some help,' and elaborate on the type or timing only if prompted.",
    "When asked about high school, discuss social experiences instead of grades or classes, e.g., 'I mostly remember hanging out with friends.",
    "When asked about hobbies, respond with something general like 'I stay busy' and elaborate only if the interviewer asks for specifics.",
    "When asked for final thoughts, say, 'There’s more, but I don’t think it’s important,' leaving the interviewer to decide whether to probe further.",
    "Say you’re not sure if you’re allergic to anything but mention a reaction to something vague, like 'I think I had a rash once from peanuts.'",
    "When asked about family history of psychiatric conditions, mention only general issues (if any) (e.g., 'My mom had health problems') and omit specific details about conditions unless prompted."
    
]

# NAME_REGIONS = [
#     "bg_BG",  # Bulgarian (Bulgaria)
#     "cs_CZ",  # Czech (Czech Republic)
#     "de_DE",  # German (Germany)
#     "dk_DK",  # Danish (Denmark)
#     "el_GR",  # Greek (Greece)
#     "en_AU",  # English (Australia)
#     "en_CA",  # English (Canada)
#     "en_GB",  # English (Great Britain)
#     "en_US",  # English (United States)
#     "es_ES",  # Spanish (Spain)
#     "es_MX",  # Spanish (Mexico)
#     "fa_IR",  # Persian (Iran)
#     "fi_FI",  # Finnish (Finland)
#     "fr_FR",  # French (France)
#     "hi_IN",  # Hindi (India)
#     "hr_HR",  # Croatian (Croatia)
#     "it_IT",  # Italian (Italy)
#     "ja_JP",  # Japanese (Japan)
#     "ko_KR",  # Korean (South Korea)
#     "lt_LT",  # Lithuanian (Lithuania)
#     "lv_LV",  # Latvian (Latvia)
#     "ne_NP",  # Nepali (Nepal)
#     "nl_NL",  # Dutch (Netherlands)
#     "no_NO",  # Norwegian (Norway)
#     "pl_PL",  # Polish (Poland)
#     "pt_BR",  # Portuguese (Brazil)
#     "pt_PT",  # Portuguese (Portugal)
#     "ru_RU",  # Russian (Russia)
#     "sl_SI",  # Slovene (Slovenia)
#     "sv_SE",  # Swedish (Sweden)
#     "tr_TR",  # Turkish (Turkey)
#     "uk_UA",  # Ukrainian (Ukraine)
#     "zh_CN",  # Chinese (China)
#     "zh_TW"   # Chinese (Taiwan)

# Middle Eastern Regions
MIDDLE_EASTERN_REGIONS = [
    "fa_IR",  # Persian - Iran
    "he_IL"   # Hebrew - Israel
]
# European Regions
EUROPEAN_REGIONS = [
    "cs_CZ",  # Czech - Czech Republic
    "da_DK",  # Danish - Denmark
    "de_AT",  # German - Austria
    "de_CH",  # German - Switzerland
    "de_DE",  # German - Germany
    "el_GR",  # Greek - Greece
    "en_CA",  # English - Canada
    "en_US",   # English - United States
    "en_GB",  # English - United Kingdom
    "en_IE",  # English - Ireland
    "es_ES",  # Spanish - Spain
    "fi_FI",  # Finnish - Finland
    "fr_CA",  # French - Canada (often linked to Europe)
    "fr_CH",  # French - Switzerland
    "fr_FR",  # French - France
    "hr_HR",  # Croatian - Croatia
    "hu_HU",  # Hungarian - Hungary
    "hy_AM",  # Armenian - Armenia
    "it_IT",  # Italian - Italy
    "nl_BE",  # Dutch - Belgium
    "nl_NL",  # Dutch - Netherlands
    "no_NO",  # Norwegian - Norway
    "pl_PL",  # Polish - Poland
    "pt_PT",  # Portuguese - Portugal
    "ro_RO",  # Romanian - Romania
    "ru_RU",  # Russian - Russia
    "sk_SK",  # Slovak - Slovakia
    "sv_SE",  # Swedish - Sweden
    "uk_UA"   # Ukrainian - Ukraine
]

# East Asian Regions
EAST_ASIAN_REGIONS = [
    "ja_JP",  # Japanese - Japan
    "ko_KR",  # Korean - South Korea
    "zh_CN",  # Chinese - China
    "zh_TW"   # Chinese - Taiwan
]

# South Asian Regions
SOUTH_ASIAN_REGIONS = [
    "en_IN",  # English - India
    "az_AZ",  # Azerbaijan
    "en_BD",  # English - Bangladesh
    "bn_BD",  # Bengali - Bangladesh
    "hi_IN",  # Hindi - India
    "ka_GE",  # Georgian - Georgia (sometimes culturally connected to South Asia)
    "ne_NP",  # Nepali - Nepal
    "ta_IN"   # Tamil - India
]

# Southeast Asian Regions
SOUTHEAST_ASIAN_REGIONS = [
    "en_MS",  # English - Malaysia
    "en_PH",  # English - Philippines
    "fil_PH", # Filipino - Philippines
    "id_ID",  # Indonesian - Indonesia
    "th_TH",  # Thai - Thailand
    "tl_PH",  # Tagalog - Philippines
    "vi_VN"   # Vietnamese - Vietnam
]

# Latin American Regions
LATIN_AMERICAN_REGIONS = [
    "es_AR",  # Spanish - Argentina
    "es_CL",  # Spanish - Chile
    "es_CO",  # Spanish - Colombia
    "es_MX",  # Spanish - Mexico
    "pt_BR"   # Portuguese - Brazil
]

# African Regions
AFRICAN_REGIONS = [
    "zu_ZA"   # Zulu - South Africa
]

# Other Regions (General or Multiple Locations)
OTHER_REGIONS = [
    "en_AU",  # English - Australia
    "en_NZ",  # English - New Zealand
]

