import json
import streamlit as st
from streamlit.components.v1 import html

from PIL import Image
import base64
from io import StringIO 
import logging
import requests
import pprint
from util import include_css

from decouple import config

SERVICE_ENDPOINT = config('SERVICE_ENDPOINT')
PAGE_ICON = config('PAGE_ICON')
PAGE_IMAGE = config('PAGE_IMAGE')
GITHUB_REPO = config('GITHUB_REPO')
DESCRIPTION = config('DESCRIPTION').replace("\\n", "\n") % (GITHUB_REPO,)
agree_on_showing_additional_information = True

EXAMPLE_FOLDER = "https://github.com/WSE-research/DTD2RDFConverter/blob/main/examples"
EXAMPLE_DTD = "https://github.com/WSE-research/DTD2RDFConverter/blob/main/examples/note.dtd?raw=true"
EXAMPLE_DTD_NAME = "note.dtd"
EXAMPLE_XML_0 = "https://github.com/WSE-research/DTD2RDFConverter/blob/main/examples/note1.xml?raw=true"
EXAMPLE_XML_0_NAME = "note1.xml"
EXAMPLE_XML_1 = "https://github.com/WSE-research/DTD2RDFConverter/blob/main/examples/note2.xml?raw=true"
EXAMPLE_XML_1_NAME = "note2.xml"

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

st.set_page_config(layout="wide", initial_sidebar_state="expanded",
    page_title="XML to RDF converter by using the corresponding DTD file",
    page_icon=Image.open(PAGE_ICON)
)
include_css(st, ["css/stFileUploadDropzone.css", "css/style_github_ribbon.css", "css/style_menu_logo.css", "css/stDownloadButton.css"])

def post_xml_and_dtd_to_server(xml_file_content, dtd_file_content, language, prefix, accept_mime_type):
    request_url = SERVICE_ENDPOINT + "xml2rdf"
    
    payload = {
        'xml': xml_file_content, 
        'dtd': dtd_file_content,
        'lang': language
    }
    
    if prefix != None:
        payload['prefix'] = prefix
    
    headers = {
        "Accept": accept_mime_type
    }
    
    results = requests.post(request_url, json=payload, verify=False, headers=headers)

    logging.info("================================= ")
    logging.info("request_url: " + request_url)
    logging.info("headers: ")
    logging.info(pprint.pformat(headers, indent=2))
    logging.info("payload: ")    
    logging.info(json.dumps(payload, indent=2))
    logging.info("results: ")    
    logging.info(pprint.pformat(results))
    logging.info(pprint.pformat(results.text))
    logging.info("================================= ")
    
    return results

@st.cache_data
def download_examples_from_github(url):
    results = requests.get(url, verify=False)
    return results.text

with st.sidebar:
    with open(PAGE_IMAGE, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")
        st.sidebar.markdown(
            f"""
            <div style="display:table;margin-top:-10%;margin-bottom:15%;text-align:center">
                <a href="{GITHUB_REPO}" title="go to GitHub repository"><img src="data:image/png;base64,{image_data}" style="width:66%;"></a>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    st.sidebar.markdown("### Parameters")
    
    label = "Define the output format of the generated RDF data"
    st.sidebar.markdown("#### {}".format(label))
    output_format_key = st.sidebar.selectbox(label=label, options=["RDF Turtle", "RDF XML", "JSON-LD"], index=0, label_visibility="collapsed")
    output_format = {
        "RDF Turtle": {
            "mime_type": "text/turtle",
            "file_extension": "ttl",
            "code_highlight": "turtle"
        },
        "RDF XML": {
            "mime_type": "application/rdf+xml",
            "file_extension": "xml",
            "code_highlight": "xml"            
        },
        "JSON-LD": {
            "mime_type": "application/ld+json",
            "file_extension": "json",
            "code_highlight": "json"
        }
    }.get(output_format_key)
    
    label = "Define the language tag for string literals in the XML files"
    st.sidebar.markdown("#### {}".format(label))
    language = st.sidebar.text_input(label=label, value="en", max_chars=5, label_visibility="collapsed")
    
    label = "Prefix for the generated URIs of the RDF data"
    st.sidebar.markdown("""
        #### {}
    """.format(label))
    prefix = st.sidebar.text_input(label=label, value="https://example.org#", label_visibility="collapsed")            

    st.sidebar.markdown("""----""")
    st.sidebar.markdown("### [Examples](%s)" % (EXAMPLE_FOLDER,))
    st.sidebar.download_button(
        label="DTD file",
        data=download_examples_from_github(EXAMPLE_DTD),
        file_name=EXAMPLE_DTD_NAME,
        mime='text/xml'
    )
    st.sidebar.download_button(
        label="XML file 1",
        data=download_examples_from_github(EXAMPLE_XML_0),
        file_name=EXAMPLE_XML_0_NAME,
        mime='text/xml'
    )
    st.sidebar.download_button(
        label="XML file 2",
        data=download_examples_from_github(EXAMPLE_XML_1),
        file_name=EXAMPLE_XML_1_NAME,
        mime='text/xml'
    )
        
    st.sidebar.markdown("""----""")
    st.sidebar.subheader("Visualization")
    agree_on_showing_additional_information = not st.checkbox(
        'minimize layout', value=(not agree_on_showing_additional_information))


# introduce the tool
page_header = """### XML to RDF converter by using the corresponding DTD file

{}                    
""".format(DESCRIPTION)

# show the page header only if the user is not minimizing the layout
if agree_on_showing_additional_information:
    with st.container():
        st.markdown(page_header, unsafe_allow_html=True)
else:
    include_css(st, ["css/remove_space_around_streamlit_body.css"])

st.markdown("#### Upload a DTD file")
uploaded_dtd_file = st.file_uploader("Upload one XML DTD file that should be used for the transformation.", accept_multiple_files=False, label_visibility="collapsed", type="dtd")
uploaded_dtd_file_contents = None

if uploaded_dtd_file is not None:
    
    if uploaded_dtd_file.name.endswith(".dtd"):
        stringio = StringIO(uploaded_dtd_file.getvalue().decode("utf-8"))
        uploaded_dtd_file_contents = stringio.read()
        number_of_lines = len(uploaded_dtd_file_contents.splitlines())
        expander_label = f"uploaded DTD file: {uploaded_dtd_file.name} ({number_of_lines} lines)"
        with st.expander(expander_label, expanded=False):
            st.markdown("### Given DTD data")
            st.code(uploaded_dtd_file_contents, language='xml')

    else:
        st.error("Uploaded file " + uploaded_dtd_file.name + " is not a DTD file.")
    


st.markdown("#### Upload one or more XML files that should be transformed with the DTD")
uploaded_xml_files = st.file_uploader("Choose XML files that should be transformed", accept_multiple_files=True, label_visibility="collapsed", type="xml")

st.markdown("#### Transformed RDF data")
if len(uploaded_xml_files) == 0 or uploaded_dtd_file_contents is None:
    st.warning("Please upload one DTD file and at least one XML file.")
else:
    counter = 0
    for uploaded_xml_file in uploaded_xml_files:
        if uploaded_xml_file.name.endswith(".xml"):
            stringio = StringIO(uploaded_xml_file.getvalue().decode("utf-8"))
            plain_xml_data = stringio.read()
            number_of_lines = len(plain_xml_data.splitlines())
            result = post_xml_and_dtd_to_server(plain_xml_data, uploaded_dtd_file_contents, language, prefix, output_format.get("mime_type"))
            rdf_filename = '.'.join(uploaded_xml_file.name.split(".")[:-1]) + "." + output_format.get("file_extension")
            
            if result.status_code == 200 and result is not None and result.text is not None:
                processing_ok = True
                processing_icon = "🆗"
                processing_text = "uploaded XML file was processed successfully"
            else:
                processing_ok = False
                processing_icon = "🚫"
                processing_text = "uploaded XML file could NOT be processed"
                
            st.markdown(f"##### {processing_icon} {uploaded_xml_file.name}")
            expander_label_xml = f"uploaded {uploaded_xml_file.name} ({number_of_lines} lines)"
            with st.expander(expander_label_xml, expanded=False):
                st.code(plain_xml_data, language='xml')    

            number_of_lines = len(result.text.splitlines())            
            expander_label_rdf = f"transformed {rdf_filename} ({number_of_lines} lines)"
            if processing_ok is True:
                with st.expander(expander_label_rdf, expanded=False):
                    st.code(result.text, language=output_format.get("code_highlight"))

                st.download_button(
                    label="Download data as {} file '{}'".format(output_format_key, rdf_filename),
                    data=result.text,
                    file_name=rdf_filename,
                    mime=output_format.get("mime_type"),
                    key="download" + str(counter)
                )
                counter += 1
        else:
            st.error("Uploaded file " + uploaded_xml_file.name + " is not an XML file.")
    

st.markdown("""
---
Brought to you by the [<img style="height:3ex;border:0" src="https://avatars.githubusercontent.com/u/120292474?s=96&v=4"> WSE research group](http://wse.technology/) at the [Leipzig University of Applied Sciences](https://www.htwk-leipzig.de/).

See our [GitHub team page](http://wse.technology/) for more projects and tools.
""", unsafe_allow_html=True)

with open("js/change_menu.js", "r") as f:
    javascript = f.read()
    html(f"<script style='display:none'>{javascript}</script>")

html("""
<script>
parent.window.document.querySelectorAll("section[data-testid='stFileUploadDropzone']").forEach(function(element) {
    element.classList.add("fileDropHover")   
});

github_ribbon = parent.window.document.createElement("div");            
github_ribbon.innerHTML = '<a id="github-fork-ribbon" class="github-fork-ribbon right-bottom" href="%s" target="_blank" data-ribbon="Fork me on GitHub" title="Fork me on GitHub">Fork me on GitHub</a>';
if (parent.window.document.getElementById("github-fork-ribbon") == null) {
    parent.window.document.body.appendChild(github_ribbon.firstChild);
}
</script>
""" % (GITHUB_REPO,))