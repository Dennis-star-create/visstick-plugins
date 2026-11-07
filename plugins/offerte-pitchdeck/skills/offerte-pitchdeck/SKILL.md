---
name: offerte-pitchdeck
description: Maakt van een klantgesprek (transcript, aantekeningen, een mailwisseling of een Drive-document) in één keer een offerte in Word (docx) en een pitchdeck van 8 slides in PowerPoint (pptx), in de eigen huisstijl, met prijzen uit de eigen prijslijst en bedragen die het script zelf uitrekent. Verzint geen prijzen of toezeggingen: wat ontbreekt wordt [INVULLEN]. Kan een begeleidende mail als concept klaarzetten, verstuurt nooit zelf. Gebruik bij "offerte-pitchdeck", "maak een offerte van dit gesprek", "zet dit gesprek om in een offerte en deck", "maak een voorstel voor <klant>".
---

# Offerte en pitchdeck uit een gesprek

Deze skill maakt van één klantgesprek twee bestanden:

- `offerte-<nummer>.docx`: een complete offerte in de huisstijl van de
  gebruiker, met situatie, doelen, aanpak, planning, prijstabel met btw,
  voorwaarden en akkoordregel.
- `pitchdeck-<nummer>.pptx`: 8 slides voor het vervolggesprek: titel, situatie,
  doelen, aanpak, planning, investering, waarom wij, volgende stap.

De gebruiker leest beide na en stuurt ze zelf. **De skill verstuurt nooit
iets.**

## 0. Voorbereiding

1. **Werkmap.** De standaard is `~/offerte-pitchdeck/`.
2. **Instellingen.** Lees `instellingen.md` in de werkmap. Ontbreekt het?
   - In een gesprek: stel de vragen uit `instellingen-voorbeeld.md` (naast deze
     SKILL.md), één blok tegelijk. Vraag om een logo (png of jpg) en kopieer
     het naar de werkmap. Schrijf daarna het bestand en ga verder.
   - Zonder gebruiker (geplande run): stop en meld dat de instellingen eerst
     ingevuld moeten worden.
3. **Script.** Het script staat in `scripts/maak_documenten.py` naast deze
   SKILL.md. Controleer of `python3 -c "import docx, pptx"` werkt. Zo niet,
   vraag of je `python3 -m pip install --user python-docx python-pptx` mag
   draaien. Weigert de gebruiker, stop dan.
4. **Nummer.** Lees `register.csv` in de werkmap, of maak het aan:
   ```
   datum,nummer,klant,onderwerp,totaal_excl,map
   ```
   Het nieuwe offertenummer volgt het patroon uit de instellingen (standaard
   `<jaar>-<volgnummer van 3 cijfers>`).

## 1. Het gesprek ophalen

Vraag waar het gesprek staat, als de gebruiker dat niet al zei. Mogelijk zijn:

- **Een bestand**: een transcript (Teams, Zoom, Google Meet, Fireflies, Otter),
  aantekeningen, een spraakmemo die al is uitgeschreven. Lees het helemaal.
- **Google Drive** (connector): zoek op klantnaam of datum, lees het document.
- **Mail** (Gmail- of Outlook-connector): zoek de thread met de klant, lees
  alle berichten, ook de aanvraag.
- **Geplakte tekst** in het gesprek.

Kun je de bron niet openen, omdat een koppeling ontbreekt? Zeg welke koppeling
er nodig is en stop. Gok niet.

Zoek daarna, als er een mailkoppeling is, of er eerder contact was met dit
bedrijf (eerdere offertes, afspraken). Neem alleen feiten over die je echt leest.

## 2. Uit het gesprek halen

Haal deze punten eruit en schrijf ze kort op, in de taal van de klant:

| Punt | Wat |
|---|---|
| klant | bedrijf, contactpersoon, adres als bekend |
| situatie | 2 tot 5 punten: hoe het nu is, wat er knelt |
| doelen | 2 tot 5 punten: wat de klant wil bereiken, in zijn woorden |
| aanpak | 2 tot 4 fases met naam, wat er gebeurt en duur |
| planning | start, mijlpalen, deadline van de klant |
| regels | wat er geleverd wordt, met aantal en eenheid |
| waarom wij | 3 punten, uit de instellingen, gekozen op wat deze klant belangrijk vond |
| volgende stap | één concrete stap met datum als die genoemd is |

Regels:
- **Prijzen alleen uit de prijslijst** in de instellingen. Staat een onderdeel
  er niet in, of noemde de klant een ander bedrag? Zet `"prijs": null`. Het
  script maakt daar `[INVULLEN]` van. Reken nooit zelf een prijs uit.
- **Geen toezeggingen** die niet in het gesprek of de instellingen staan:
  geen levertijden, garanties of kortingen.
- Wat onduidelijk is, vraag je aan de gebruiker voordat je de bestanden maakt.
  Hooguit drie vragen in één bericht. In een run zonder gebruiker laat je het
  open als `[INVULLEN]`.
- Btw: standaard 21%, tenzij de prijslijst een ander tarief noemt. Bij een
  klant in het buitenland of een verlegde regeling: vraag het.

## 3. Bestanden maken

1. Maak de map `~/offerte-pitchdeck/offertes/<datum>-<klant-kort>/`.
2. Schrijf daarin `offerte.json` met deze opbouw:
   ```json
   {
     "huisstijl": {"primair": "#1B2A4A", "accent": "#F28C28", "lettertype": "Calibri", "logo": "~/offerte-pitchdeck/logo.png"},
     "bedrijf": {"naam": "", "adres": "", "postcode_plaats": "", "email": "", "telefoon": "", "website": "", "kvk": "", "btw": "", "iban": "", "contactpersoon": ""},
     "klant": {"bedrijf": "", "contact": "", "adres": "", "postcode_plaats": ""},
     "offerte": {
       "nummer": "", "datum": "", "geldig_tot": "", "onderwerp": "", "aanspreekvorm": "u",
       "aanhef_naam": "", "inleiding": "",
       "situatie": [], "doelen": [],
       "aanpak": [{"fase": "", "omschrijving": "", "duur": ""}],
       "planning": "",
       "regels": [{"omschrijving": "", "aantal": 1, "eenheid": "st", "prijs": 0, "btw": 21}],
       "voorwaarden": [], "volgende_stap": ""
     },
     "waarom_wij": [],
     "afsluiting": "Met vriendelijke groet,\n\nNaam\nBedrijf"
   }
   ```
   - `aanspreekvorm`: `u` of `je`, uit de instellingen of zoals de klant in het gesprek sprak. De koppen volgen dit.
   - `onderwerp`: de belofte aan de klant in maximaal 8 woorden, niet "Offerte".
   - `inleiding`: 2 tot 3 zinnen, verwijst naar het gesprek.
   - Slides tonen hooguit 5 punten en 4 fases. Houd elk punt onder de 90 tekens.
3. Draai:
   ```
   python3 <pad naar deze skill>/scripts/maak_documenten.py offerte.json <map>
   ```
   Het script rekent subtotaal, btw per tarief en totaal uit, en meldt hoeveel
   `[INVULLEN]` er nog in staan.
4. **Controleer het resultaat.** Is `soffice` (LibreOffice) aanwezig? Zet dan
   beide om naar pdf en bekijk de pagina's als afbeelding. Let op: tekst die
   buiten een vak loopt, een lege slide, een verkeerde naam. Pas de JSON aan en
   draai opnieuw. Zonder LibreOffice: open de bestanden niet zelf, maar zeg dat
   de gebruiker ze moet nalopen.
5. Zet een regel in `register.csv`.

## 4. Begeleidende mail (optioneel)

Als de gebruiker het wil en er een mailkoppeling is die **concepten** kan maken:
schrijf een korte mail van 4 tot 6 zinnen aan de contactpersoon (dank voor het
gesprek, wat er in de offerte staat, de volgende stap) en zet die als **concept**
klaar, als antwoord in de bestaande thread als die er is. Kan de koppeling geen
bijlage toevoegen? Zeg dan dat de gebruiker de twee bestanden zelf toevoegt.
Kan ze geen concepten maken? Geef de mailtekst dan in het gesprek. Verstuur nooit.

## 5. Overzicht

Sluit af met:

```
Offerte <nummer> voor <klant>: <onderwerp>
Totaal: <excl. btw> excl. btw (<incl.> incl. btw)
Bestanden: <pad docx>, <pad pptx>
Nog invullen: <aantal> plekken: <waar>
Concept-mail: klaar in <mailbox> / niet gemaakt
Nalopen: prijzen, planning, naam en adres van de klant.
```

## Wat de skill nooit doet

- Offertes of mails versturen.
- Prijzen, kortingen, levertijden of garanties verzinnen.
- Gegevens van de ene klant in de offerte van een andere klant gebruiken.
- Bestanden buiten de werkmap wijzigen of verwijderen.
