import requests
import pkg_resources
from lxml import html
from xblock.core import XBlock
from xblock.fields import Boolean, Scope
from xblock.fragment import Fragment
from xblockutils.resources import ResourceLoader
from xblockutils.studio_editable import StudioEditableXBlockMixin
from xblockutils.studio_editable import StudioContainerXBlockMixin
loader = ResourceLoader(__name__)

class BrowserlockproctorXBlock(StudioContainerXBlockMixin,XBlock):
    has_proctoring = Boolean(default=False, scope=Scope.user_state_summary, help="Whether the proctoring is enabled")
    has_children = True
    
    def student_view(self, context=None):
        html_str =pkg_resources.resource_string(__name__, "static/html/browserlockproctor.html").decode('utf-8')
        frag = Fragment(str(html_str).format(block=self))
        parent=XBlock.get_parent(self)
        css_str=pkg_resources.resource_string(__name__, "static/css/browserlockproctor.css").decode('utf-8')
        frag.add_css(str(css_str)) 
        child_frags = self.runtime.render_children(block=self, view_name='student_view')
        children=child_frags
        html = loader.render_template('static/html/sequence.html', children)
        frag.add_content(html)
        frag.add_frags_resources(child_frags)
        # children=child_frags
        # html = loader.render_template(
        #     'static/html/sequence.html', children)
        # frag.add_content(html)
        # frag.add_frags_resources(child_frags)
        js_str=pkg_resources.resource_string(__name__, "static/js/src/browserlockproctor.js").decode('utf-8')
        frag.add_javascript(str(js_str))
        frag.initialize_js('BrowserlockproctorXBlock')
        
        return frag

    def studio_view(self, context=None):
        html_str = """
            <div class="proctoring-studio-container">
                <h2>Proctoring settings</h2>
                <p><label><input type="checkbox" name="has_proctoring" value="true" {% if self.has_proctoring %}checked{% endif %}> Enable proctoring for this exam</label></p>
            </div>
        """
        frag = Fragment(html_str)
        frag.add_css("""
            .proctoring-studio-container {
                border: 1px solid #ccc;
                padding: 10px;
                margin-bottom: 20px;
            }
        """)
        frag.add_javascript("""
            $(function() {
                $('input[name="has_proctoring"]').on('change', function() {
                    handlerUrl = runtime.handlerUrl(null, 'studio_submit');
                    $.ajax({
                        type: "POST",
                        url: handlerUrl,
                        data: JSON.stringify({
                            "has_proctoring": this.checked
                        }),
                        success: function() {
                            // Reload the page
                            location.reload();
                        }
                    });
                });
            });
        """)
        return frag
    

    @XBlock.handler
    def studio_submit(self, request, suffix=''):
        """
        The handler for the studio submit action
        """
        self.has_proctoring = request.POST.get("has_proctoring") == "true"
        return {"result": "success"}
    

    def studio_submit(self, data, suffix=''):
        """
        The handler for the studio save action
        """
        self.has_proctoring = data.get("has_proctoring") == "true"


    def get_proctoring_status(self):
        """
        Get the proctoring status for the current user
        """
        if self.has_proctoring:
            # TODO: Check if the user's browser is in locked mode
            return True
        else:
            return False
        
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("BrowserlockproctorXBlock",
             """<browserlockproctor/>
             """),
            ("Multiple BrowserlockproctorXBlock",
             """<vertical_demo>
                <browserlockproctor/>
                <browserlockproctor/>
                <browserlockproctor/>
                </vertical_demo>
             """),
        ]
