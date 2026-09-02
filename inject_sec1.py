import re
filepath = r"C:\Users\Admin\Desktop\TEST REPORT PRODUCTION final\templates\belt_scale.html"
with open(filepath, 'r', encoding='utf-8') as f:
    html = f.read()

section1 = '''
                    <!-- SECTION 1: SYSTEM METADATA -->
                    <div class="section-box active-step" id="step-box-1" style="margin-top: 24px;">
                        <div class="section-box-title">
                            <i class="fa-solid fa-heading"></i> 1. System Metadata
                        </div>
                        <div class="grid-col-2">
                            <div class="input-group"><label>Job No.</label><input type="text" name="job_no" id="job_no"></div>
                            <div class="input-group"><label>Customer</label><input type="text" name="customer" id="customer"></div>
                            <div class="input-group"><label>Capacity (TPH)</label><input type="text" name="capacity" id="capacity"></div>
                            <div class="input-group"><label>Conveyor No.</label><input type="text" name="conveyor_no" id="conveyor_no"></div>
                        </div>
                    </div>
'''

html = html.replace("<!-- STEP PROGRESS BAR -->", section1)

# Also I need to remove the garbage Tacho block that was left over because my previous regex didn't catch it!
# The garbage tacho block is right before my injected "<!-- SECTION 1:" wait, no, I injected Section 2!
# Let me just clear everything between Section 1 and Section 2!

start_str = "Conveyor No.</label><input type=" + '"' + "text" + '"' + " name=" + '"' + "conveyor_no" + '"' + " id=" + '"' + "conveyor_no" + '"' + "></div>\n                        </div>\n                    </div>"
end_str = "<!-- SECTION 1"  # wait, I injected section 2 earlier. Let's find it.
import re
filepath = r"C:\Users\Admin\Desktop\TEST REPORT PRODUCTION final\templates\belt_scale.html"
with open(filepath, 'r', encoding='utf-8') as f:
    html = f.read()

section1 = '''
                    <!-- SECTION 1: SYSTEM METADATA -->
                    <div class="section-box active-step" id="step-box-1" style="margin-top: 24px;">
                        <div class="section-box-title">
                            <i class="fa-solid fa-heading"></i> 1. System Metadata
                        </div>
                        <div class="grid-col-2">
                            <div class="input-group"><label>Job No.</label><input type="text" name="job_no" id="job_no"></div>
                            <div class="input-group"><label>Customer</label><input type="text" name="customer" id="customer"></div>
                            <div class="input-group"><label>Capacity (TPH)</label><input type="text" name="capacity" id="capacity"></div>
                            <div class="input-group"><label>Conveyor No.</label><input type="text" name="conveyor_no" id="conveyor_no"></div>
                        </div>
                    </div>
'''

html = html.replace("<!-- STEP PROGRESS BAR -->", section1)

# Also I need to remove the garbage Tacho block that was left over because my previous regex didn't catch it!
# The garbage tacho block is right before my injected "<!-- SECTION 1:" wait, no, I injected Section 2!
# Let me just clear everything between Section 1 and Section 2!

start_str = "Conveyor No.</label><input type=" + '"' + "text" + '"' + " name=" + '"' + "conveyor_no" + '"' + " id=" + '"' + "conveyor_no" + '"' + "></div>\n                        </div>\n                    </div>"
end_str = "<!-- SECTION 1"  # wait, I injected section 2 earlier. Let's find it.