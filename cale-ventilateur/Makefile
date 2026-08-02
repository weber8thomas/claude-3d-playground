PARTS := cale gabarit gabarit_fente essai mod_hubs
SRC   := src/cale_ventilateur.scad

.PHONY: all verify slice stl export web serve params clean help

verify:            ## Les 7 gardes : WARNING, maillage, zmin, cotes, volume, percages, cible
	@python3 tools/verify.py

slice:             ## Garde 8 : trancher pour de vrai (aucun support, tout pont fait)
	@python3 tools/slice_check.py

buses:             ## Comparer les buses 0,4 / 0,6 / 0,8 : temps MESURES par piece
	@python3 tools/buses.py $(PART)

web:               ## Viewer 3D autonome (build/index.html) : la piece a l'oeil
	@python3 tools/gallery.py
	@mkdir -p docs && cp build/index.html docs/viewer.html
	@echo "  copie versionnee -> docs/viewer.html (lien GitHub Pages)"
	@echo "  ouvre  build/index.html  (autonome, marche en double-clic)  ou  make serve"

serve: web         ## Sert build/ en local (http://localhost:8000/index.html)
	@echo "  -> http://localhost:8000/index.html   (Ctrl-C pour arreter)"
	@cd build && python3 -m http.server 8000

stl: $(addprefix build/,$(addsuffix .stl,$(PARTS)))  ## Rendre tous les STL

export:            ## STL versionnes (stl/) pour telechargement / lien GitHub
	@mkdir -p stl
	@for p in $(PARTS); do \
	  openscad -o stl/$$p.stl -D "part=\"$$p\"" $(SRC) 2>&1 | grep -Ei 'WARNING|ERROR' && exit 1 || true; \
	  echo "  -> stl/$$p.stl"; done

build/%.stl: $(SRC) | build
	@openscad -o $@ -D 'part="$*"' $< 2>&1 | grep -Ei 'WARNING|ERROR' && exit 1 || true
	@echo "  -> $@"

params:            ## Afficher toutes les cotes derivees
	@openscad --export-format=stl -o /dev/null -D 'part="cale"' $(SRC) 2>&1 \
	  | sed -n 's/^ECHO: "\(.*\)"$$/  \1/p'

build:
	@mkdir -p build

clean:
	@rm -rf build

help:
	@grep -E '^[a-z]+:.*?##' $(MAKEFILE_LIST) | awk -F':.*?## ' '{printf "  %-10s %s\n",$$1,$$2}'
