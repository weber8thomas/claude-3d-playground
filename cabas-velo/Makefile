PARTS := a b hook hooks3 gauge hinge_test plate
SRC   := src/cabas_velo.scad

.PHONY: all verify stl profile web serve clean params

verify:            ## Toutes les gardes : WARNING, Volumes, zmin, encombrement
	@python3 tools/verify.py

web:               ## Viewer 3D autonome (build/index.html) : chaque iteration a l'oeil
	@python3 tools/gallery.py
	@cp build/index.html docs/viewer.html
	@echo "  copie versionnee -> docs/viewer.html (lien GitHub / htmlpreview)"
	@echo "  ouvre  build/index.html  (autonome, marche en double-clic)  ou  make serve"

serve: web         ## Sert build/ en local (http://localhost:8000/index.html)
	@echo "  -> http://localhost:8000/index.html   (Ctrl-C pour arreter)"
	@cd build && python3 -m http.server 8000

stl: $(addprefix build/,$(addsuffix .stl,$(PARTS)))  ## Rendre tous les STL

export:            ## STL versionnes (stl/) pour telechargement / lien GitHub
	@mkdir -p stl
	@for p in hook hooks3 a b gauge plate; do \
	  openscad -o stl/$$p.stl -D "part=\"$$p\"" $(SRC) 2>&1 | grep -Ei 'WARNING|ERROR' && exit 1 || true; \
	  echo "  -> stl/$$p.stl"; done

build/%.stl: $(SRC) | build
	@openscad -o $@ -D 'part="$*"' $< 2>&1 | grep -Ei 'WARNING|ERROR' && exit 1 || true
	@echo "  -> $@"

profile:           ## Tracer le profil 2D du crochet, tube en place
	@python3 tools/profile_plot.py

params:            ## Afficher toutes les cotes derivees
	@openscad -o /dev/null -D 'part="hook"' $(SRC) 2>&1 | sed -n 's/^ECHO: "\(.*\)"$$/  \1/p'

build:
	@mkdir -p build

clean:
	@rm -rf build

help:
	@grep -E '^[a-z]+:.*?##' $(MAKEFILE_LIST) | awk -F':.*?## ' '{printf "  %-10s %s\n",$$1,$$2}'
