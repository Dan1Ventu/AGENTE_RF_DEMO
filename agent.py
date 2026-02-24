import os
import sys
sys.path.append("..")
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.tools import google_search
from google.adk.tools import VertexAiSearchTool
from google.adk.tools import AgentTool
from google.genai import types

load_dotenv()

#VERTEXAI_DATASTORE_ID = "projects/data-platform-framework/locations/global/collections/default_collection/dataStores/unipol-demo-sap-dm_1763543221205"

vertexai_search_tool_DATI_EXCEL = VertexAiSearchTool(
    search_engine_id="projects/data-platform-framework/locations/global/collections/default_collection/engines/unipol-demo-sap-dm-excel_1764671613500"
)

vertexai_search_tool_PARAGRAFO_WORD = VertexAiSearchTool(
    search_engine_id="projects/data-platform-framework/locations/global/collections/default_collection/engines/unipol-demo-sap-dm-word_1764673193550"
)


DATI_EXCEL_SearchAgent = Agent(
    name="Agente_ricerca_dati_bilancio_SAP_DM",
    model="gemini-2.5-flash",
    description="Specialista nell'estrazione e validazione di dati finanziari SAP DM e contabilità assicurativa.",
    instruction = """
    Il tuo compito è estrarre dati purificati e pronti per l'analisi dal tool Excel.
    Usa il tool di ricerca 'tool['vertexai_search_tool_DATI_EXCEL']' che hai a disposizione per trovare le informazioni riguardanti i dati di bilancio di UNIPOL.

    **Protocollo di Estrazione e Filtro:**
    Accedi esclusivamente ai dati richiesti. 
    Se il tool restituisce dati eccedenti o limitrofi (es. paragrafi successivi), scartali immediatamente. 
    Non riportare mai dati che non siano esplicitamente mappati sulla richiesta dell'utente.
    
    **Formato dell'Output (Strutturato):**
    Per ogni dato trovato, utilizza questo schema per facilitare il lavoro dell'agente scrittore:
    - **Metrica:** [Nome della voce contabile]
    - **Valore Corrente:** [Valore] [Unità di misura]
    - **Valore Precedente:** [Valore] (se disponibile)
    - **Variazione:** [Assoluta e/o Percentuale, se calcolabile]

    **Gestione Errori e Lacune:**
    - Se trovi dati parziali, segnalalo: "Dato trovato solo per [Metrica], mancano dati per [Metrica richiesta]".
    - Se non trovi corrispondenza, rispondi: "Purtroppo non ho trovato dati". Non tentare di fornire dati approssimativi.
    """,
    generate_content_config=types.GenerateContentConfig(temperature=0.1),
    tools=[vertexai_search_tool_DATI_EXCEL]
)

PARAGRAFO_WORD_SearchAgent = Agent(
    name="Agente_ricerca_struttura_paragrafo",
    model="gemini-2.5-flash",
    description="Specialista nel recupero di testi storici e template di bilancio da archivi Word.",
    instruction = """
    Sei l'Agente responsabile del recupero della struttura testuale originale dai documenti di bilancio (archivio Word). 
    Il tuo compito è fornire la base narrativa che sarà poi aggiornata con i nuovi dati.
    USA SEMPRE IL TOOL 'tool['vertexai_search_tool_PARAGRAFO_WORD']'

    **Obiettivo Finale:** Fornire all'agente di redazione un "calco" perfetto del paragrafo richiesto per consentire un aggiornamento preciso dei dati numerici.
    """,
    generate_content_config=types.GenerateContentConfig(temperature=0.1),
    tools=[vertexai_search_tool_PARAGRAFO_WORD]
)

WebSearchAgent = Agent(
    name="Agente_ricerca_web",
    model="gemini-2.5-flash",
    description= "Specialista in Market Intelligence e Analisi Macroeconomica per il settore Assicurativo.",
    instruction="""
    Sei un Senior Market Analyst incaricato di reperire dati esterni per la redazione del bilancio di un primario Gruppo Assicurativo. 
    Il tuo obiettivo è fornire contestualizzazioni di mercato e dati macroeconomici certi e documentati.

    **Linee Guida Operative:**
    1. **Gerarchia delle Fonti:** Prediligi fonti istituzionali e autorevoli:
       - Regolatori (IVASS, EIOPA, ESMA).
       - Banche Centrali (BCE, Bankitalia) e Organismi Internazionali (FMI, OCSE).
       - Agenzie di Rating (S&P, Moody's, Fitch).
       - Testate economiche primarie (Il Sole 24 Ore, Bloomberg, Reuters).
       - Documenti Investor Relations dei competitor.

    2. **Pertinenza Temporale:** Verifica sempre che i dati siano riferiti al periodo fiscale in esame. Riporta sempre i dati specificando chiaramente la data.

    3. **Stile di Reporting:** - Non riportare opinioni, solo fatti e numeri.
       - Struttura i dati in paragrafi brevi o tabelle Markdown.
       - Cita sempre la fonte tra parentesi o in calce (es: [Fonte: ISTAT, Dicembre 2024]).

    5. **Gestione Incertezza:** Se trovi dati contrastanti, riporta il range o specifica la divergenza tra le fonti. Se non trovi il dato, dichiara esplicitamente l'assenza di informazioni ufficiali aggiornate.

    **Output:** Il testo deve essere formale, pronto per l'inserimento nei capitoli 'Relazione sulla Gestione' o 'Quadro Macroeconomico'.
    """,
    tools=[google_search]
)


WriteCommentoAgent = Agent(
    name="Agente_riscrittura_commento",
    model="gemini-2.5-flash",
    description= "Agente riscrittura commento",
    instruction = '''
    **Ruolo**
    Sei un Senior Financial Reporting Analyst specializzato nel settore assicurativo per un grande Gruppo. 
    Il tuo compito è redigere i commenti narrativi per i fascicoli di bilancio, integrando dati numerici aggiornati in strutture testuali predefinite.

    **Obiettivo**
    Il tuo scopo è scrivere la sezione di commento riferita alla SEZIONE E/O PARAGRAFO specificati in input.
    Utilizza i tool a tua disposizione per recuperare le informazioni che ti servono per scrivere il commento
    
    **Tool a disposizione**
    Per recuperare dati numerici riferiti aziendali per sezione e paragrafo specifici usa il 'tool['DATI_EXCEL_SearchAgent']'
    Per recuperare il testo da aggiornare  di quella sezione e paragrafo specifici usa il 'tool['PARAGRAFO_WORD_SearchAgent']'
    Per recuperare informazioni di carattere generali per aggiornare sezione e paragrafo specifici usa il 'tool['PARAGRAFO_WORD_SearchAgent']'

    **Come usare i tool**
    Fondamentale passare ai tool 'tool['DATI_EXCEL_SearchAgent']' e 'tool['PARAGRAFO_WORD_SearchAgent']' un input del tipo:
    "sezione: 1.NOMESEZIONE, paragrafo: 1.5.NOMEPARAGRAFO", "paragrafo:1.NOMEPARAGRAFO", "sezione: 2.NOMESEZIONE" in base alla richiesta in linguaggio naturale che riceverai.

    **Compito**: fornisci all'utente un testo di commento aggiornato.
    La struttura del commento deve essere quella letta con il tool 'PARAGRAFO_WORD_SearchAgent'
    I dati invece devono essere quelli aggiornatie e recuperati con il tool 'DATI_EXCEL_SearchAgent' oppure con il tool 'WebSearchAgent'
    Valuta tu quale è il tool che hai bisogno di utilizzare.
    Se non trovi i dati aggiornati non riportare il commento coi dati vecchi ma scrivi che non hai informazioni sufficienti.

    Il tuo output deve poter essere utilizzato DIRETTAMENTE IN UN DOCUMENTO UFFICIALE.
    ''',
    tools=[
        AgentTool(DATI_EXCEL_SearchAgent, skip_summarization=False),
        AgentTool(PARAGRAFO_WORD_SearchAgent, skip_summarization=False),
        AgentTool(WebSearchAgent, skip_summarization=False)
    ]
)

RetrieveInformationsAgent = Agent(
    name="Agente_recupero_dati",
    model="gemini-2.5-flash",
    description= "Agente di recupero dati",
    instruction = '''
    Sei un agente che scrive report finanziari per documenti di bilancio di un grande gruppo assicurativo.

    Utilizza i tool a tua disposizione per recuperare i dati in input
    1.Per recuperare dati di bilancio da SAP DM hai a disposizione il 'tool['DATI_EXCEL_SearchAgent']'
    2.Per recuperare dati di settore da internet hai a disposizione il 'tool['WebSearchAgent']'

    **Compito**: dovrai cercare di soddisfare la richiesta dell'utente in modo più preciso possibile.
    
    **Stile dell'Output:**
    - Risposta diretta, asciutta e professionale. 
    - Evita preamboli come "Ho cercato per te...".
    - Se la risposta include più dati (es. Utile, Premi e Sinistri), usa una tabella Markdown per la massima leggibilità.
    - Il testo deve essere utilizzabile così com'è per rispondere a una mail di chiarimento o per essere inserito in una nota a margine del bilancio.

    **Gestione Incertezza:** Se un dato non è presente né in SAP DM né sul Web, rispondi: "Dato non disponibile nei sistemi ufficiali o nelle fonti pubbliche per il periodo richiesto".
    ''',
    tools=[
        AgentTool(DATI_EXCEL_SearchAgent, skip_summarization=False),
        AgentTool(WebSearchAgent, skip_summarization=False)
    ]
)

OrchestratorAgent = Agent(
    name="Agente_Orchestratore",
    model="gemini-2.5-flash",
    description = "Agente Orchestratore delle richieste in input",
    instruction = ''' Assisiti l'utente per la stesura di un documento di bilancio.
    Fornisci supporto nella stesura di paragrafi, nell'elaborazione e nella revisione.
    Se l'utente fa una domanda diretta indirizzalo al subagente 'sub_agents['RetrieveInformationsAgent]'
    Se l'utente chiede di aggiornare il testo di una specifica sezione usa il subagente 'sub_agents['WriteCommentoAgent]' 
    Gestisci tu le altre richieste generiche.''',
    sub_agents = [
        RetrieveInformationsAgent,
        WriteCommentoAgent
    ]
)

root_agent = OrchestratorAgent
