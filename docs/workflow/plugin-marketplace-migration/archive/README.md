# Archive - Plugin Marketplace Migration

**Directory**: `docs/workflow/plugin-marketplace-migration/archive/`
**Scopo**: File storici e documenti preliminari del progetto

---

## Contenuto

### migration-plan-original.md (20 KB)
**Data creazione**: 2026-01-02
**Status originale**: "READY FOR BASELINE"
**Descrizione**: Piano di migrazione preliminare/iniziale

Questo documento rappresenta la **prima versione** del piano di migrazione di AI-Craft a plugin Claude Code. È stato creato come documento di visione iniziale e successivamente espanso nel progetto completo.

**Evoluzione**:
- **2026-01-02**: Creato `migration-plan.md` nella cartella `plugin-migration/`
- **2026-01-05**: Espanso in `baseline.yaml` con misurazioni dettagliate
- **2026-01-05**: Dettagliato in `roadmap.yaml` (8 fasi, 33 step, 55-70 ore)
- **2026-01-05**: Implementato in 33 file JSON step-by-step (`steps/*.json`)
- **2026-01-05-06**: Reviewato con 35 adversarial reviews complete
- **2026-01-06**: Archiviato come riferimento storico

**Superseded da**:
- `../baseline.yaml` - Baseline dettagliato con metriche
- `../roadmap.yaml` - Roadmap completo 8 fasi
- `../steps/*.json` - 33 step implementativi dettagliati
- `../adversarial-reviews/` - 35 file di review critica

**Perché archiviato**:
- Contenuto completamente espanso e superato dal progetto attuale
- Mantiene valore storico per comprendere l'evoluzione del progetto
- Documenta la visione iniziale vs implementazione finale

---

## Struttura Progetto Attuale

Il piano originale è stato evoluto in:

```
plugin-marketplace-migration/
├── baseline.yaml              ← Baseline dettagliato (espansione del piano)
├── roadmap.yaml               ← 8 fasi, 33 step (dettaglio completo)
├── steps/                     ← 33 file JSON implementativi
│   └── *.json                 ← Ogni step con TDD, refactoring, review
├── adversarial-reviews/       ← 35 file di critical review
│   ├── README.md
│   ├── INDEX.md
│   ├── MASTER_SUMMARY.md      ← 5 critical blockers identificati
│   └── ...
└── archive/                   ← Questa directory
    ├── README.md              ← Questo file
    └── migration-plan-original.md
```

---

## Differenze Chiave: Piano Originale vs Progetto Attuale

### Piano Originale (migration-plan.md)
- **Formato**: Documento Markdown descrittivo
- **Scope**: Visione generale e categorizzazione
- **Dettaglio**: Alto livello, concettuale
- **Fasi**: Non strutturate in fasi formali
- **Metriche**: Criteri di successo generici
- **Review**: Nessuna review adversarial

### Progetto Attuale (baseline + roadmap + steps)
- **Formato**: YAML + JSON strutturati
- **Scope**: Implementazione esecutiva step-by-step
- **Dettaglio**: Granulare con TDD, refactoring, quality gates
- **Fasi**: 8 fasi formali con dipendenze
- **Metriche**: Baseline quantitativo + 7 success criteria misurabili
- **Review**: 35 adversarial reviews con risk scoring

---

## Valore Storico

Questo documento è prezioso per:
1. **Comprendere l'evoluzione**: Come una visione iniziale diventa un progetto esecutivo
2. **Confrontare approcci**: Piano descrittivo vs roadmap strutturato
3. **Validare completezza**: Verificare che tutti i concetti iniziali sono stati implementati
4. **Lezioni apprese**: Analizzare gap tra visione e implementazione

---

## Note

**Cartella originale**: `docs/workflow/plugin-migration/` (eliminata dopo archiviazione)
**Data archiviazione**: 2026-01-06
**Archiviato da**: Lyra (AI-Craft Framework)
**Motivo**: Consolidamento documentazione progetto

---

**Status**: ARCHIVED
**Riferimento attivo**: Usa `../roadmap.yaml` e `../baseline.yaml` per progetto corrente
