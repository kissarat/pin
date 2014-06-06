-- Deleting referensed pins (from removed boards) from pins_categories
DELETE from pins_categories
       where pin_id IN
       (SELECT id from pins where board_id IN
       (SELECT id from BOARDS where (name <> 'Things to get'
       AND name <> 'Places to visit' AND name <> 'Food to eat') OR name IS NULL));
-- Deleting pins related to removed boards
DELETE from pins where board_id IN
       (SELECT id from BOARDS where (name <> 'Things to get'
       AND name <> 'Places to visit'
       AND name <> 'Food to eat') OR name IS NULL);
-- Deleting removed boards themselves
DELETE from BOARDS where (name <> 'Things to get'
       AND name <> 'Places to visit'
       AND name <> 'Food to eat') OR name IS NULL;
