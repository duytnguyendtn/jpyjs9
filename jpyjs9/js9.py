"""
JS9 wrapper to be used in Jupyter/IPython notebooks.
Some of the ideas were adopted from jjs9
"""

# ignore socketio connection error
import logging
#logging.getLogger('root').setLevel(logging.ERROR)
import json
from pathlib import Path
import subprocess
import uuid
import weakref

import ipywidgets as ipw
from sidecar import Sidecar

from pyjs9 import JS9 as JS9_ 


_JS9Refs = {}

class JS9(JS9_):

    def __init__(self, side=False, *args, **kwargs):
        """Start or connect to an instance of JS9

        Parameters:
        -----------
        host: 'http://localhost:2718',
        id: 'JS9',
        multi: False,
        pageid: None,
        maxtries: 5,
        delay: 1,
        debug: False,
        side: False, Set true to start in a side windown in jupyter
        frame_url: 'http://localhost:8888/js9', the url to the js9 app
        width: 600
        height: 600
        """
        # append the main docstring from parent
        JS9.__init__.__doc__ += JS9_.__init__.__doc__


        if len(args) > 1:
            id = args[1]
            args = (args[0],) + args[2:]
        else:
            id = kwargs.pop('id', str(uuid.uuid4())[:4])

        if len(args) == 7:
            debug = args[6]
        else:
            debug = kwargs.get('debug', False)

        if debug:
            logger = logging.getLogger()
            logger.setLevel(logging.DEBUG)

        # extra parameter
        # Derive URL subfolder path from Jupyter URL:
        logging.debug("Evaluating default frame url...")
        try:
            subproc_out = subprocess.check_output(["jupyter", "lab", "list", "--json"])
            # Extract out only the json element by finding the first '{' and last '}'
            current_jupyter_session = subproc_out[subproc_out.index('{'):subproc_out.rfind('}')+1]
            jupyter_base_path = Path(json.loads(current_jupyter_session)['base_url'])
            frame_url_fallback = (jupyter_base_path / "js9").as_posix()
            logging.debug("Successfully retrieved Jupyter base_url path")
        except Exception as e:
            # Use our usual fallback frame url
            frame_url_fallback = "/js9"
            logging.debug(f"Failed to retrieve Jupyter URL: {str(e)}, using default fallback")
        frame_url = kwargs.get('frame_url', frame_url_fallback)
        logging.debug(f"Using frame URL: {frame_url}")

        width  = kwargs.get('width', 600)
        height = kwargs.get('height', 700)


        ref = _JS9Refs.get(id, None)
        if ref is not None:
            logging.debug(f'Recovering instance {id}')
            ref = ref()
            logging.debug(f'Recovered instance {id}')
            
        # attach the JS9 window
        html = f"<iframe src='{frame_url}?frameid={id}' width={width} height={height}></iframe>"
        self.ipw_obj = ipw.widgets.HTML(value = html)

        self.sc = None
        if side:
            # open a side window 
            layout = ipw.Layout(width=f'{width}px', height=f'{height}px')
            self.sc = Sidecar(title=f'JS9-{id}', layout=layout)
            with self.sc:
                display(self.ipw_obj)
        else:
            display(self.ipw_obj)


        if ref is None:
            logging.debug(f'Starting a new instance {id}')
            _JS9Refs[id] = weakref.ref(self)
        
        # initialize the parent JS9 class, first remove our added keys
        for k in ['frame_url', 'width', 'height']:
            kwargs.pop(k, None)
        logging.debug(f'Calling parent for {id}')
        # TBF: Properly handle race condition
        logging.debug(f'Sleeping to avoid race condition')
        import time; time.sleep(5)
        super(JS9, self).__init__(id=f'JS9-{id}', multi=True, *args, **kwargs)


    def close(self):
        # close the display as well as the js9 connection
        self.ipw_obj.close()
        if self.sc is not None:
            self.sc.close()
        super(JS9, self).close()
