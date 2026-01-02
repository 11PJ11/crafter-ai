# 📖 COMANDO: Analisi Plotholes Narrativi

> **Creato**: 2025-12-30
> **Scopo**: Template riutilizzabile per analisi sistematica dei plotholes narrativi
> **Status**: Draft - Punto di integrazione futuro

---

## 🎯 Principi Base

### Principle of Least Resistance
- Quando un task diventa ripetitivo e difficile → DELEGA alla macchina
- Templatizza il più possibile

### Prompt Engineering
- Chiaro e specifico
- Strutturato: definisci parametri e sezioni
- Crea un comando riutilizzabile
- Descrivi il deliverable: forma e struttura dell'output
- Outcome chiaro: perché il deliverable è importante?
- Criteri di accettazione rigorosi

---

## 📋 Parametri

```
NOVEL_TITLE = "Titolo del romanzo"
AUTHOR = "Nome autore"
GENRE = "Fantasy/Sci-Fi/Thriller/etc." (opzionale - aiuta il contesto)
MANUSCRIPT_PATH = "path/al/file.md o .txt" (se disponibile)
```

---

## 📄 Template Output

```markdown
# Analisi Plotholes: [NOVEL_TITLE]

**Autore**: [AUTHOR]
**Data Analisi**: [DATA]
**Analista**: Claude Code

---

## 🎯 Executive Summary
[Sintesi dei plotholes principali identificati - max 3-4 punti]

---

## 📊 Plotholes Identificati

### 1. [Titolo Plothole]

**Categoria**: [Logica Interna / Continuity / Character Motivation / World-Building / Timeline]

**Severità**: 🔴 Critica / 🟡 Media / 🟢 Minore

**Descrizione**:
[Descrizione chiara dell'inconsistenza narrativa]

**Evidenza Testuale**:
- Capitolo/Scena X: [citazione o riferimento]
- Capitolo/Scena Y: [contraddizione]

**Impatto Narrativo**:
[Come questo plothole influenza la sospensione dell'incredulità del lettore]

**Possibili Soluzioni**:
1. [Opzione A - descrizione]
2. [Opzione B - descrizione]
3. [Opzione C - descrizione]

**Note**:
[Considerazioni aggiuntive]

---

[Ripetere per ogni plothole]

---

## 🔍 Analisi per Categoria

### Logica Interna
[Riepilogo plotholes di logica interna]

### Character Motivation
[Riepilogo inconsistenze motivazionali]

### World-Building
[Riepilogo problemi di costruzione del mondo]

### Timeline & Continuity
[Riepilogo problemi temporali e di continuità]

---

## 💡 Raccomandazioni Prioritarie

1. **Alta Priorità** (plotholes critici che rompono la narrazione)
   - [Elenco]

2. **Media Priorità** (miglioramenti consigliati)
   - [Elenco]

3. **Bassa Priorità** (dettagli minori)
   - [Elenco]

---

## 📝 Note Metodologiche

**Approccio Utilizzato**:
[Descrizione del metodo di analisi - es. "lettura lineare", "analisi tematica", "focus su world-building"]

**Limitazioni**:
[Eventuali limitazioni dell'analisi - es. "analisi basata su manoscritto parziale", "senza accesso a note dell'autore"]

**Distinguishing Factor**:
[Chiarire se i "plotholes" sono effettivamente errori o scelte narrative intenzionali che potrebbero essere risolte in seguito]
```

---

## 🤖 Comando

```
Per favore analizza [NOVEL_TITLE] di [AUTHOR] identificando potenziali plotholes narrativi.

Se disponibile, leggi il manoscritto in [MANUSCRIPT_PATH].
Se non disponibile, basati sulla trama e informazioni che ti fornirò.

Scrivi un file markdown chiamato `plothole-analysis-[NOVEL_TITLE-slug]-[DATA].md` seguendo il TEMPLATE sopra definito.

Concentrati su:
- Inconsistenze logiche interne alla narrazione
- Contraddizioni tra eventi o descrizioni
- Motivazioni dei personaggi che non reggono
- Violazioni delle regole del world-building stabilite
- Problemi di timeline o continuità
```

---

## 🎯 Outcome

Voglio identificare **sistematicamente i punti deboli narrativi** del mio romanzo **prima della pubblicazione** in modo da:
- Rafforzare la coerenza interna della storia
- Migliorare la sospensione dell'incredulità
- Prevenire critiche evitabili
- Mantenere la fiducia del lettore nella narrazione

---

## ✅ Criteri di Accettazione

1. **Evidence-Based Analysis**:
   - ❌ NO: "Questo plothole confonde il 70% dei lettori"
   - ✅ SÌ: "Contraddizione testuale tra Capitolo 3 (pag. 45) e Capitolo 12 (pag. 203)"

2. **Distinzione tra Plothole e Mistero Intenzionale**:
   - Chiarire se un'apparente inconsistenza potrebbe essere un mistero da rivelare successivamente
   - Segnalare quando non è possibile distinguere (es. "Potrebbe essere intenzionale se risolto nel Cap. X")

3. **Citazioni Precise**:
   - Ogni plothole DEVE riferirsi a passaggi specifici del testo
   - Se il testo non è disponibile, basarsi su sinossi/outline forniti dall'utente

4. **No Speculazioni Quantitative**:
   - Non inventare percentuali di impatto
   - Non fare affermazioni su "quanto questo danneggia la storia" senza base oggettiva
   - Usare severità qualitativa (Critica/Media/Minore) con giustificazione

5. **Soluzioni Praticabili**:
   - Ogni plothole identificato deve avere almeno 2 possibili soluzioni concrete
   - Le soluzioni devono rispettare la coerenza narrativa esistente

6. **Scope Limitato**:
   - Focus su plotholes oggettivi (inconsistenze logiche)
   - NON includere preferenze stilistiche o suggerimenti creativi generici

---

## 💾 Come Usare

### Opzione A - Con manoscritto

```bash
# Salva questo template come skill in .claude/skills/plothole-analysis.md
# Poi esegui:
NOVEL_TITLE="Il Regno delle Ombre"
AUTHOR="Mario Rossi"
MANUSCRIPT_PATH="./manuscript/draft-v3.md"

[Incolla il comando personalizzato]
```

### Opzione B - Senza manoscritto (brainstorming da outline)

```
"Ho scritto un romanzo fantasy dove [breve sinossi].
Analizza la trama per identificare potenziali plotholes usando il template di analisi."
```

---

## 🔮 Prossimi Passi per Integrazione

- [ ] Creare skill Claude Code riutilizzabile (`/dw:plothole`)
- [ ] Testare su romanzo campione
- [ ] Integrare con workflow 5D-Wave esistente
- [ ] Aggiungere supporto per analisi multi-volume (serie)
- [ ] Considerare integrazione con Mikado Method per tracking correzioni plotholes

---

## 📚 Esempio Correlato

Questo template segue il pattern dell'esempio "Critiche Letterarie":

```
TARGET = "tutte le critiche letterarie"
AUTHOR = "Titania Blesh"
TEMPLATE = <...>

Comando: Per favore recupera [TARGET] per [AUTHOR].
Scrivi un file .md basato sul [TEMPLATE] dandogli tu un nome adeguato.

Outcome: Raccogliere feedback strutturati per migliorare o refutare le critiche.

Accetazione:
- Solo siti e riviste autorevoli
- No dichiarazioni senza evidenza empirica
```
