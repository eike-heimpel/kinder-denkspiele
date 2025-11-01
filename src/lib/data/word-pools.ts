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
    ],

    'extra-hard': [
        // Very complex animals and nature
        'Stachelschwein', 'Kolibri', 'Tausendfüßler', 'Seepferdchen', 'Schmetterlingsraupe',
        'Glühwürmchen', 'Silberreiher', 'Regenwurm', 'Schneckenhaus', 'Honigbiene',

        // Complex compound words
        'Sonnenblume', 'Schneeballschlacht', 'Geburtstagsfeier', 'Schokoladenkuchen',
        'Fußballspiel', 'Weihnachtsbaum', 'Regenwolke', 'Sonnenschein',
        'Adventskranz', 'Kinderzimmer', 'Spielplatzrutsche', 'Sandkasten',

        // Scientific and educational terms (kid-appropriate)
        'Dinosaurier', 'Teleskop', 'Mikroskop', 'Vulkan', 'Kristall',
        'Magnet', 'Roboter', 'Astronaut', 'Weltraum', 'Universum',

        // Abstract concepts and activities
        'Experiment', 'Entdeckung', 'Abenteuer', 'Fantasie', 'Kreativität',
        'Freundschaft', 'Geburtstag', 'Überraschung', 'Erlebnis', 'Erinnerung',

        // Complex natural phenomena
        'Erdbeben', 'Lawine', 'Tornado', 'Nordlicht', 'Sternschnuppe',
        'Vollmond', 'Halbmond', 'Sonnenaufgang', 'Sonnenuntergang', 'Morgenröte',

        // Complex objects and tools
        'Kompass', 'Fernglas', 'Schubkarre', 'Leiter', 'Werkzeugkasten',
        'Taschenlampe', 'Kompass', 'Sandburg', 'Drachen', 'Seifenblase',

        // Advanced food and cooking
        'Pfannkuchen', 'Apfelkuchen', 'Blaubeere', 'Brombeere', 'Kokosnuss',
        'Rosine', 'Mandel', 'Haselnuss', 'Zimt', 'Vanille',

        // Complex places and environments
        'Gebirge', 'Dschungel', 'Wüste', 'Höhle', 'Gletscher',
        'Wasserfall', 'Vulkan', 'Schlucht', 'Hügel', 'Tal'
    ]
};
