import sys

html_file = 'templates/belt_scale.html'
with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

replacement = """                                    </tbody>
                                </table>
                            </div>
                            
                            <!-- Resolution Inputs -->
                            <div style="margin-top: 20px; background: rgba(0,0,0,0.02); padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0;">
                                <h4 style="margin-top: 0; margin-bottom: 15px; font-size: 14px; color: #0f172a;"><i class="fa-solid fa-magnifying-glass-chart"></i> Resolution Settings</h4>
                                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;">
                                    <div class="input-group">
                                        <label>Load (L) Resolution</label>
                                        <input type="text" name="res_l" placeholder="e.g. 0.01">
                                    </div>
                                    <div class="input-group">
                                        <label>Speed (S) Resolution</label>
                                        <input type="text" name="res_s" placeholder="e.g. 0.1">
                                    </div>
                                    <div class="input-group">
                                        <label>Rate (R) Resolution</label>
                                        <input type="text" name="res_r" placeholder="e.g. 1">
                                    </div>
                                    <div class="input-group">
                                        <label>Totaliser (T) Resolution</label>
                                        <input type="text" name="res_t" placeholder="e.g. 10">
                                    </div>
                                </div>
                                <p style="margin: 8px 0 0 0; font-size: 12px; color: #64748b; font-style: italic;">* Units (Kg/m, m/s, TPH, Tonnes) will be automatically appended to your values in the PDF.</p>
                            </div>
                            
                            <div class="wizard-actions">"""

content = content.replace("                                    </tbody>\n                                </table>\n                            </div>\n                            <div class=\"wizard-actions\">", replacement)

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated HTML")
