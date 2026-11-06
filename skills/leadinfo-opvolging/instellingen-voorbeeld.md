# Instellingen Leadinfo-opvolging

Kopieer dit bestand naar `~/leadinfo-opvolging/instellingen.md` en vul het in.
De skill vraagt er ook zelf naar bij de eerste run in een gesprek.

## Afzender
- naam: Voornaam Achternaam
- functie: Eigenaar
- bedrijf: Bedrijfsnaam B.V.
- website: voorbeeld.nl
- eigen e-mailadres: naam@voorbeeld.nl
- telefoon (in de handtekening, optioneel): 06 …
- taal: Nederlands
- aanspreekvorm: je            # je of u

## Handtekening
```
Met vriendelijke groet,

Voornaam Achternaam
Bedrijfsnaam
voorbeeld.nl
```

## Voorbeeldmail (voor de toon)
Plak hier één mail die je zelf aan een prospect stuurde. De skill leest geen
andere verzonden mails.
```
Hoi …,
…
```

## Afspraak
- afspraaklink (optioneel): https://…   # bijv. Calendly, Microsoft Bookings, Google-agenda
- gespreksduur: 15 minuten

## Aanbod: welke pagina hoort bij welke dienst
Eén regel per pagina of groep pagina's. Hiermee kiest de skill het onderwerp.
- /prijzen, /contact: sterk signaal, concreet een kennismaking voorstellen
- /dienst-a: korte omschrijving van wat dienst A oplevert
- /dienst-b: …
- alleen de homepage: algemeen, wat het bedrijf voor hun branche doet

## Uitsluitlijst
Bedrijven of domeinen die nooit een opvolgmail krijgen (klanten, partners,
concurrenten).
- klant-a.nl
- Partner B

## Werking
- werkmap: ~/leadinfo-opvolging
- autopilot_bcc: nee          # ja als Autopilot jou in BCC zet (dan zoekt de skill sneller)
- zoekperiode_dagen: 14
- wachtdagen: 5               # zo veel dagen na de Autopilot-mail volgt de skill op
- max_dagen: 30               # daarna geen opvolging meer
- max_per_run: 15
- rapportage_downloaden: nee  # ja = de downloadlink uit "Rapportage LeadInfo" ophalen
- bezoek_noemen: nee          # ja = alleen "je keek onlangs op onze website", als Autopilot dat ook deed
- afmeldzin: Liever geen mail meer van mij? Laat het weten, dan hoor je niets meer.
