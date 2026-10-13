# project-readme Specification

## Purpose
README del repositorio en inglés y en español, enlazados entre sí y con la web.
## Requirements
### Requirement: README bilingüe
`README.md` SHALL estar en inglés y `README.es.md` en español, con el mismo contenido (instalación, uso, configuración, solución de problemas, actualizaciones, limitaciones, desarrollo, publicación y créditos). Cada uno MUST enlazar al otro al principio y enlazar a la web del proyecto.

#### Scenario: Enlaces cruzados
- **WHEN** un visitante abre el README en GitHub
- **THEN** ve en la primera línea un enlace a la otra versión y a la web

#### Scenario: Mismas secciones
- **WHEN** se comparan los dos README
- **THEN** tienen el mismo número de secciones de segundo y tercer nivel

