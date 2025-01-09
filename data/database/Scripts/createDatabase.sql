CREATE DATABASE IF NOT EXISTS banco_recomendacion;
USE banco_recomendacion;

CREATE TABLE profile_data (
                              id INT AUTO_INCREMENT PRIMARY KEY,
                              informacion_academica_ponderacion INT NULL,
                              idioma_ponderacion INT NULL,
                              experiencia_laboral_ponderacion INT NULL,
                              habilidades_ponderacion INT NULL,
                              personal_map_id INT NULL
);

CREATE TABLE profile_model (
                               id INT AUTO_INCREMENT PRIMARY KEY,
                               personal_map_data_id INT NULL,
                               FOREIGN KEY (personal_map_data_id) REFERENCES profile_data(id)
);

ALTER TABLE profile_data
    ADD CONSTRAINT fk_personal_map_id FOREIGN KEY (personal_map_id) REFERENCES profile_model(id);

CREATE TABLE academic_info (
                               id INT AUTO_INCREMENT PRIMARY KEY,
                               area_de_estudio VARCHAR(255) NULL,
                               area_de_estudio_ponderacion INT NULL,
                               nivel_de_estudio VARCHAR(255) NULL,
                               nivel_de_estudio_ponderacion INT NULL,
                               estado_de_estudio VARCHAR(255) NULL,
                               estado_de_estudio_ponderacion INT NULL,
                               profile_data_id INT,
                               FOREIGN KEY (profile_data_id) REFERENCES profile_data(id)
);

CREATE TABLE language_skill (
                                id INT AUTO_INCREMENT PRIMARY KEY,
                                idioma VARCHAR(255) NULL,
                                idioma_ponderacion INT NULL,
                                nivel_escritura VARCHAR(255) NULL,
                                nivel_escritura_ponderacion INT NULL,
                                nivel_habla VARCHAR(255) NULL,
                                nivel_habla_ponderacion INT NULL,
                                profile_data_id INT,
                                FOREIGN KEY (profile_data_id) REFERENCES profile_data(id)
);

CREATE TABLE work_experience (
                                 id INT AUTO_INCREMENT PRIMARY KEY,
                                 nombre_del_puesto VARCHAR(255) NULL,
                                 nombre_del_puesto_ponderacion INT NULL,
                                 jerarquia VARCHAR(255) NULL,
                                 jerarquia_ponderacion INT NULL,
                                 nombre_de_la_empresa VARCHAR(255) NULL,
                                 nombre_de_la_empresa_ponderacion INT NULL,
                                 ubicacion_de_la_empresa VARCHAR(255) NULL,
                                 ubicacion_de_la_empresa_ponderacion INT NULL,
                                 tipo_de_empresa VARCHAR(255) NULL,
                                 tipo_de_empresa_ponderacion INT NULL,
                                 area_de_trabajo VARCHAR(255) NULL,
                                 area_de_trabajo_ponderacion INT NULL,
                                 actualmente_trabajo_aqui VARCHAR(255) NULL,
                                 actualmente_trabajo_aqui_ponderacion INT NULL,
                                 tiempo_de_trabajo VARCHAR(255) NULL,
                                 tiempo_de_trabajo_ponderacion INT NULL,
                                 profile_data_id INT,
                                 FOREIGN KEY (profile_data_id) REFERENCES profile_data(id)
);

CREATE TABLE skills (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        habilidades_blandas TEXT NULL,
                        habilidades_tecnicas TEXT NULL,
                        habilidades_blandas_ponderacion INT NULL,
                        habilidades_tecnicas_ponderacion INT NULL,
                        profile_data_id INT,
                        FOREIGN KEY (profile_data_id) REFERENCES profile_data(id)
);

CREATE TABLE profile_model_tags (
                                    id INT AUTO_INCREMENT PRIMARY KEY,
                                    profile_model_id INT,
                                    tag VARCHAR(255) NOT NULL,
                                    FOREIGN KEY (profile_model_id) REFERENCES profile_model(id)
);
CREATE TABLE personal_info (
                               id INT AUTO_INCREMENT PRIMARY KEY,
                               nombre_completo VARCHAR(255) NULL,
                               numero_cedula VARCHAR(50) NULL,
                               telefono VARCHAR(50) NULL,
                               correo VARCHAR(255) NULL,
                               linkedin VARCHAR(255) NULL,
                               estado_civil VARCHAR(50) NULL,
                               fecha_nacimiento DATE NULL,
                               edad INT NULL,
                               aspiracion_salarial FLOAT NULL,
                               tipo_sangre VARCHAR(10) NULL,
                               direccion VARCHAR(255) NULL,

                               profile_model_id INT, -- Clave foránea hacia profile_model
                               FOREIGN KEY (profile_model_id) REFERENCES profile_model(id)
);