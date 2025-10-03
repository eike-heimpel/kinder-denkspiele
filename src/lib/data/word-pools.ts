import type { WordPool } from '$lib/types';

export const germanWordPools: WordPool = {
    easy: [
        // Animals (Tiere)
        'Hund', 'Katze', 'Maus', 'Vogel', 'Fisch', 'Pferd', 'Kuh', 'Schwein',
        'Hase', 'Fuchs', 'Bär', 'Löwe', 'Elefant', 'Affe', 'Giraffe', 'Zebra',

        // Colors (Farben)
        'Rot', 'Blau', 'Grün', 'Gelb', 'Orange', 'Lila', 'Rosa', 'Braun',
        'Schwarz', 'Weiß', 'Grau',

        // Food (Essen)
        'Apfel', 'Banane', 'Brot', 'Käse', 'Milch', 'Ei', 'Pizza', 'Kuchen',
        'Saft', 'Wasser', 'Butter', 'Honig', 'Reis', 'Nudeln',

        // Body parts (Körper)
        'Hand', 'Fuß', 'Kopf', 'Auge', 'Ohr', 'Nase', 'Mund', 'Arm',
        'Bein', 'Bauch', 'Haar',

        // Common objects (Gegenstände)
        'Ball', 'Buch', 'Auto', 'Haus', 'Tür', 'Fenster', 'Tisch', 'Stuhl',
        'Bett', 'Lampe', 'Uhr', 'Telefon', 'Baum', 'Blume', 'Sonne', 'Mond',
        'Stern', 'Wolke', 'Regen', 'Schnee'
    ],

    hard: [
        // More complex animals
        'Schmetterling', 'Schildkröte', 'Eichhörnchen', 'Pinguin', 'Delfin',
        'Krokodil', 'Nashorn', 'Nilpferd', 'Flamingo', 'Papagei',

        // Weather and nature
        'Gewitter', 'Regenbogen', 'Nebel', 'Frosch', 'Schlange', 'Spinne',
        'Marienkäfer', 'Libelle', 'Biene', 'Ameise',

        // More complex food
        'Erdbeere', 'Himbeere', 'Wassermelone', 'Schokolade', 'Marmelade',
        'Gemüse', 'Karotte', 'Tomate', 'Gurke', 'Salat', 'Zwiebel',

        // Places and locations
        'Schule', 'Garten', 'Park', 'Spielplatz', 'Strand', 'Berg',
        'Wald', 'Wiese', 'Fluss', 'See', 'Meer', 'Insel',

        // Actions and concepts
        'Lachen', 'Weinen', 'Rennen', 'Springen', 'Tanzen', 'Singen',
        'Malen', 'Spielen', 'Lesen', 'Schreiben', 'Schlafen', 'Essen',

        // More objects
        'Schere', 'Schlüssel', 'Rucksack', 'Regenschirm', 'Brille',
        'Fahrrad', 'Flugzeug', 'Schiff', 'Zug', 'Rakete', 'Luftballon',
        'Geschenk', 'Spielzeug', 'Puppe', 'Teddy'
    ]
};
