USE medikiosk;
INSERT IGNORE INTO departments(name,code,description,is_active,created_at) VALUES
('General Medicine','GENMED','General adult medicine',1,NOW()),
('Orthopaedics','ORTHO','Bones and joints',1,NOW()),
('Cardiology','CARDIO','Heart and cardiovascular care',1,NOW()),
('Pulmonology','PULMO','Respiratory care',1,NOW()),
('Neurology','NEURO','Neurological care',1,NOW()),
('Dermatology','DERMA','Skin care',1,NOW()),
('ENT','ENT','Ear nose and throat',1,NOW()),
('Gynaecology','GYNAE','Women health',1,NOW()),
('Paediatrics','PAEDS','Child health',1,NOW()),
('Ayurveda','AYUR','AYUSH/Ayurveda',1,NOW());







