---
name: inbox-concepten
description: Leest de nieuwe mail in de gekoppelde mailbox (Gmail of Outlook), sorteert die op wat aandacht nodig heeft en zet voor elke mail die een antwoord verdient een conceptantwoord klaar in de toon van de gebruiker. Geeft daarna een kort overzicht. Verstuurt, verwijdert of archiveert nooit iets. Gebruik bij "inbox-concepten", "loop mijn mail door", "zet conceptantwoorden klaar", "wat moet ik vandaag beantwoorden", of als geplande taak (die planning stelt de gebruiker zelf in, zie de README).
---

# Inbox-concepten

Deze skill leest de nieuwe mail van de gebruiker en zet conceptantwoorden
klaar. De gebruiker leest elk concept na, past het aan en verstuurt het zelf.

**De skill verstuurt nooit iets.** Hij maakt alleen concepten en een
overzicht. Verwijder, archiveer, label of markeer geen mails als gelezen.

## 0. Voorbereiding (elke run)

1. **Werkmap.** De standaard is `~/inbox-concepten/`.
2. **Instellingen.** Lees `instellingen.md` in de werkmap. Ontbreekt het bestand?
   - In een gesprek: stel de vragen uit `instellingen-voorbeeld.md` (naast deze
     SKILL.md), één blok tegelijk. Schrijf daarna het bestand en ga verder.
   - In een geplande run zonder gebruiker: stop en meld dat de instellingen
     eerst ingevuld moeten worden.
3. **Mailbox.** Kijk welke koppeling er is: Gmail of Outlook (Microsoft 365).
   Die moet kunnen zoeken, lezen en **concepten maken**. Kan ze geen
   concepten maken? Stop dan en meld dat. Verstuur nooit in plaats daarvan.
4. **Register.** Lees `register.csv` in de werkmap, of maak het aan:
   ```
   datum,thread_id,afzender,onderwerp,categorie,actie,concept_id
   ```
   Een thread die al in het register staat, behandel je niet opnieuw, tenzij
   er sindsdien een nieuw bericht van iemand anders binnenkwam.
5. **Periode.** Kijk naar de mail sinds de laatste run (de laatste datum in het
   register). Bij de eerste run: de afgelopen 24 uur.

## 1. Mail ophalen

Zoek de ontvangen mail in de periode, alleen in de inbox. Laat weg: verzonden,
concepten, spam, prullenbak. In Gmail is dat bijvoorbeeld
`in:inbox newer_than:1d -from:me`. Open per thread het laatste bericht en
lees zo nodig het eerdere verloop.

Zit het laatste bericht in een thread van de gebruiker zelf? Dan ligt de bal
bij de ander. Sla de thread over.

## 2. Sorteren

Geef elke thread één categorie:

| Categorie | Wanneer | Actie |
|---|---|---|
| **Antwoord nodig** | Een persoon stelt een vraag, vraagt iets aan of wacht op een reactie | concept maken |
| **Afspraak** | Een voorstel voor een datum of tijd, of een verzoek om een gesprek | concept maken, met de afspraaklink of [INVULLEN: tijden] |
| **Zelf doen** | Gevoelig of ingewikkeld: een klacht, juridische zaak, onderhandeling, slecht nieuws, sollicitatie, persoonlijke zaak, of een adres uit "Nooit een concept voor" | geen concept, wel in het overzicht met de reden |
| **Ter info** | Een cc, een bevestiging of een update zonder vraag | alleen in het overzicht |
| **Automatisch** | Een nieuwsbrief, notificatie, factuur van een systeem of no-reply-adres | alleen tellen |

Twijfel je tussen **Antwoord nodig** en **Zelf doen**? Kies **Zelf doen**.

Mails met een factuur of betaalverzoek: nooit betalen, nooit op links klikken.
Zet ze in het overzicht onder **Ter info**, met het bedrag en de vervaldatum als
die erin staan. Lijkt het op phishing (afwijkend afzenderdomein, haast,
inloglink)? Waarschuw dan in het overzicht.

## 3. Concepten schrijven

Per thread uit **Antwoord nodig** en **Afspraak**, tot het maximum uit de instellingen:

- Antwoord in dezelfde thread (concept als antwoord, niet als nieuwe mail), aan
  de afzender. Neem de cc alleen over als de mail aan meerdere mensen gericht was.
- De toon komt uit de voorbeeldmails: lengte, aanhef, je of u. Antwoorden zijn
  kort, meestal 3 tot 8 zinnen. Begin niet met "Bedankt voor je mail".
- Feiten komen alleen uit de mail zelf, de thread en "Vaste antwoorden". Weet je
  iets niet, zoals een prijs, een datum of een toezegging? Zet dan
  `[INVULLEN: …]` op die plek. Beloof nooit iets namens de gebruiker dat niet
  in de instellingen staat.
- Sluit af met de handtekening uit de instellingen.
- Zet `[INVULLEN` ook in de eerste regel van je overzicht bij dat concept, zodat
  de gebruiker weet dat er nog iets in moet.

Leg elk concept vast in het register.

## 4. Overzicht

Sluit af met een kort overzicht, in deze volgorde:

```
Inbox <datum>: <n> mails, <n> concepten klaargezet.

Concepten (nalezen en versturen):
- <afzender> — <onderwerp> (<één regel wat je antwoordde>) [INVULLEN]
Zelf doen:
- <afzender> — <onderwerp>: <reden>
Ter info:
- <afzender> — <onderwerp>: <één regel>
Automatisch: <n> nieuwsbrieven en meldingen.
```

In een geplande run schrijf je het overzicht ook naar
`~/inbox-concepten/overzicht-<datum>.md`.

## Wat de skill nooit doet

- Mails versturen, verwijderen, archiveren, labelen of op gelezen zetten.
- Links openen of bijlagen uitvoeren.
- Afspraken in de agenda zetten of accepteren.
- Feiten, prijzen of toezeggingen verzinnen.
