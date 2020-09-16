# panelapp

Allows for lots of operations for Panelapp queries

## Install

``` python
pip install panelapp
```

## Import

``` python
from panelapp import Panelapp
from panelapp import api
from panelapp import queries
```

## How to use

``` python
from panelapp import Panelapp

panel = Panelapp.Panel(269)        # Create panel object, confidence level defaults to 3, version is the lastest
panel.get_info()                   # Return dict with general data about the panel
panel.get_genes()                  # Return genes according to confidence level choosen when creating the panel object
panel.get_genes(3, 2, 1)           # Return genes with confidence levels 3, 2, 1 (green, amber, red)
panel.update_version("3.2", "2")   # Update the panel with version and confidence level given
panel.is_signedoff()               # Return date of signedoff or False if not signedoff
panel.get_data()                   # Return all the data the API sent, you can use that there's something that is lacking in my methods

# There's a few other bits, go look at the code, it's not complicated

from panelapp import queries

panels = queries.get_all_panels()                                         # Return dict {panel_id: Panelapp.Panel} of all panels in Panelapp
signedoff_panels = queries.get_all_signedoff_panels()                     # Return dict {panel_id: Panelapp.Panel} of signedoff panels
matches, differences = queries.compare_versions(Panelapp.Panel, "2.7")    # Return tuple of match and differences between the given panel and another panel version
panel = queries.get_signedoff_panel(269)                                  # Return panel object with latest signedoff version
```
