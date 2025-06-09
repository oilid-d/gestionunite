import streamlit as st
from datetime import datetime

# --- Session State & Authentication ---
def login_form():
    st.title("Aviation Maintenance Management Login")
    with st.form('login_form', clear_on_submit=False):
        role = st.selectbox('Select Role', ['Chief of Unit', 'ATSEP', 'Client'], key='login_role')
        username = st.text_input('Username', key='login_username')
        password = st.text_input('Password', type='password', key='login_password')
        submitted = st.form_submit_button('Login')
        if submitted:
            # Map role to username suffix for lookup
            role_suffix = {'Chief of Unit': '-CHIEF', 'ATSEP': '-ATSEP', 'Client': '-CLIENT'}
            user_key = username.strip() + role_suffix[role]
            users = {
                'chief-CHIEF': {'password': 'chief123', 'role': 'Chief of Unit', 'avatar': 'https://i.imgur.com/1Q9Z1Zm.png'},
                'houcine-ATSEP': {'password': 'atsep123', 'role': 'ATSEP', 'avatar': 'https://i.imgur.com/2z6b7Yk.png'},
                'airport1-CLIENT': {'password': 'client123', 'role': 'Client', 'avatar': 'https://i.imgur.com/3y6b7Yk.png'},
            }
            user = users.get(user_key)
            if user and password == user['password'] and user['role'] == role:
                st.session_state['authenticated'] = True
                st.session_state['role'] = user['role']
                st.session_state['username'] = user_key
                st.session_state['avatar'] = user['avatar']
                st.rerun()
            else:
                st.error('Invalid username, password, or role.')
    #st.info("Demo accounts:\nChief: chief / chief123\nATSEP: houcine / atsep123\nClient: airport1 / client123\nSelect the correct role for your username.")

def logout():
    if st.button('Logout', key='logout_btn'):
        for k in ['authenticated', 'role', 'username', 'avatar']:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()

# --- Header Layout ---
def app_header():
    col1, col2, col3 = st.columns([2,6,2])
    with col1:
        st.image('logo.png', width=80)
    with col2:
        st.title("Aviation Maintenance Management")
        # Global Search Bar
        search_query = st.text_input('Search (Airport, Mission, Drone, Problem Ref)', key='global_search', label_visibility='collapsed', placeholder='Search...')
        if search_query:
            st.info(f"Search results for: {search_query} (Demo only)")
    with col3:
        # Check for notifications
        notifications = 0
        role = st.session_state.get('role')
        
        if role == 'Chief of Unit':
            # Count new problem reports
            problems = st.session_state.get('problem_reports', [])
            new_problems = len([p for p in problems if p['status'] == 'New'])
            
            # Count new mission reports
            mission_reports = st.session_state.get('mission_reports', [])
            new_reports = len([r for r in mission_reports if r.get('status') == 'Submitted'])
            
            notifications = new_problems + new_reports
            
            # Display notification count if there are any
            col3_left, col3_right = st.columns([1,2])
            with col3_left:
                if notifications > 0:
                    st.markdown(f'<div style="background-color: red; color: white; border-radius: 50%; width: 25px; height: 25px; text-align: center; line-height: 25px; margin-top: 10px;">{notifications}</div>', unsafe_allow_html=True)
            with col3_right:
                st.image(st.session_state.get('avatar', 'https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y'), width=40)
        else:
            st.image(st.session_state.get('avatar', 'https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y'), width=40)
        st.text(st.session_state.get('username','Account'))
        logout()

# --- Chief of Unit Views ---
def chief_dashboard():
    st.subheader('Mission Tracking Dashboard')
    
    # Get missions from session state
    missions = st.session_state.get('missions', [])
    
    # Search filters
    col1, col2 = st.columns(2)
    with col1:
        airport_search = st.text_input("🔍 Filter by Airport")
    with col2:
        atsep_search = st.text_input("🔍 Filter by ATSEP")
    
    # Filter missions based on search criteria
    if airport_search or atsep_search:
        filtered_missions = []
        for m in missions:
            airport_match = not airport_search or airport_search.lower() in m['airport'].lower()
            atsep_match = not atsep_search or (
                atsep_search.lower() in m.get('groupchief', '').lower() or 
                atsep_search.lower() in m.get('pilote', '').lower() or 
                atsep_search.lower() in m.get('data_analyst', '').lower()
            )
            if airport_match and atsep_match:
                filtered_missions.append(m)
    else:
        filtered_missions = missions
    
    # Metrics
    total_missions = len(filtered_missions)
    en_cours = sum(1 for m in filtered_missions if m['status'] == 'En cours')
    done = sum(1 for m in filtered_missions if m['status'] == 'Done')
    attribue = sum(1 for m in filtered_missions if m['assignment'] == 'Accepted')
    pas_attribue = sum(1 for m in filtered_missions if m['assignment'] == 'New')
    
    # Display metrics in cards
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.metric('Total Missions', total_missions)
            st.metric('Accepted', attribue)
    with col2:
        with st.container(border=True):
            st.metric('In Progress', en_cours)
            st.metric('New', pas_attribue)
    with col3:
        with st.container(border=True):
            st.metric('Completed', done)
    
    # Filtering for table view
    status_filter = st.selectbox('Filter by Status', ['All', 'En cours', 'Done', 'New'])
    assignment_filter = st.selectbox('Filter by Assignment', ['All', 'Accepted', 'New', 'Rejected'])
    
    # Apply additional filters
    table_missions = [m for m in filtered_missions 
                     if (status_filter == 'All' or m['status'] == status_filter) 
                     and (assignment_filter == 'All' or m['assignment'] == assignment_filter)]
    
    # Prepare table data with relevant columns
    if table_missions:
        table_data = []
        for m in table_missions:
            table_data.append({
                'Reference': m['ref'],
                'Airport': m['airport'],
                'Status': m['status'],
                'Assignment': m['assignment'],
                'Start Date': m['date_start'],
                'End Date': m['date_finish'],
                'Team': f"Chief: {m['groupchief']}, Pilot: {m['pilote']}, Analyst: {m['data_analyst']}"
            })
        st.dataframe(table_data, use_container_width=True)

def chief_drone_certificates():
    st.markdown('**Certificate Management**')
    if 'show_add_cert' not in st.session_state:
        st.session_state['show_add_cert'] = False
    if st.button('Add Certificate', key='show_add_cert_btn'):
        st.session_state['show_add_cert'] = not st.session_state['show_add_cert']
    
    if st.session_state['show_add_cert']:
        with st.form('add_cert_form', clear_on_submit=True):
            cert_name = st.text_input('Certificate Name')
            validation = st.text_input('Validation Duration')
            acq_date = st.date_input('Date Acquisition')
            exp_date = st.date_input('Date Fin Expiration')
            cert_file = st.file_uploader('Upload Calibration Certificate', type=['pdf', 'png', 'jpg'])
            submitted = st.form_submit_button('Add Certificate')
            if submitted and cert_file and cert_name:
                if 'certs' not in st.session_state:
                    st.session_state['certs'] = []
                st.session_state['certs'].append({'name': cert_name, 'validation': validation, 'acq': str(acq_date), 'exp': str(exp_date), 'file': cert_file.name, 'filedata': cert_file.getvalue()})
                st.success('Certificate added!')

    certs = st.session_state.get('certs', [
        {'name': 'Calib2025', 'validation': '1 year', 'acq': '2025-01-01', 'exp': '2026-01-01', 'file': 'calib2025.pdf', 'filedata': b'Sample certificate 2025'},
        {'name': 'Calib2024', 'validation': '1 year', 'acq': '2024-01-01', 'exp': '2025-01-01', 'file': 'calib2024.pdf', 'filedata': b'Sample certificate 2024'},
    ])
    
    # Display certificates for download above the table
    st.write("Download Certificates:")
    cert_cols = st.columns(len(certs))
    for idx, (col, cert) in enumerate(zip(cert_cols, certs)):
        with col:
            st.download_button(f"⬇️ {cert['file']}", 
                             data=cert['filedata'] if cert['filedata'] else b'Sample certificate', 
                             file_name=cert['file'],
                             key=f'dl_cert_{idx}')
    
    # Display the table without download buttons
    cert_rows = []
    for cert in certs:
        cert_rows.append({
            'Name': cert['name'],
            'Validation': cert['validation'],
            'Acquisition': cert['acq'],
            'Expiration': cert['exp'],
            'File': cert['file']
        })
    st.dataframe(cert_rows, use_container_width=True)

# --- Completed Missions Reports ---
def chief_completed_missions_reports():
    st.header('Completed Mission Reports')
    st.caption('Review and manage completed mission reports')

    if 'submitted_reports' in st.session_state and st.session_state['submitted_reports']:
        # Group reports by status
        unreviewed_reports = [r for r in st.session_state['submitted_reports'] if r['status'] == 'Submitted']
        reviewed_reports = [r for r in st.session_state['submitted_reports'] if r['status'] != 'Submitted']
        
        # Show unreviewed reports first
        if unreviewed_reports:
            st.warning(f"You have {len(unreviewed_reports)} new mission report(s) to review")
            st.markdown("### New Reports Pending Review")
            for report in unreviewed_reports:
                with st.expander(f"🆕 Mission {report['ref']} - {report['airport']}", expanded=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Mission Details**")
                        st.write(f"Airport: {report['airport']}")
                        st.write(f"Start Date: {report['date_start']}")
                        st.write(f"Completion Date: {report['date_finish']}")
                        st.write(f"Mission Status: {report['mission_status']}")
                        st.write(f"Submitted: {report['timestamp']}")
                    
                    with col2:
                        st.write("**Team**")
                        st.write(f"Pilot: {report['pilote']}")
                        st.write(f"Data Analyst: {report['data_analyst']}")
                          # Add review controls
                        new_status = st.selectbox(
                            "Review Status",
                            ["Approved", "Needs Revision"],
                            key=f"review_{report['ref']}"
                        )
                        if st.button("Submit Review", key=f"submit_review_{report['ref']}"):
                            report['status'] = new_status
                            st.success(f"Report marked as {new_status}")
                            st.rerun()
                    
                    st.markdown("---")
                    st.write("**Findings**")
                    st.write(report['findings'])
                    
                    st.write("**Actions Taken**")
                    st.write(report['actions'])
                    
                    st.write("**Recommendations**")
                    st.write(report['recommendations'])
                
                # File download buttons
                col1, col2 = st.columns(2)
                with col1:
                    if report['flight_profile']['name']:
                        st.download_button(
                            "Download Flight Profile",
                            data=report['flight_profile']['data'],
                            file_name=report['flight_profile']['name'],
                            key=f"chief_dl_profile_{report['ref']}"
                        )
                with col2:
                    if report['report']['name']:
                        st.download_button(
                            "Download Mission Report",
                            data=report['report']['data'],
                            file_name=report['report']['name'],
                            key=f"chief_dl_report_{report['ref']}"
                        )

        # Show previously reviewed reports
        if reviewed_reports:
            st.markdown("### Previously Reviewed Reports")
            for report in reviewed_reports:
                with st.expander(f"Mission {report['ref']} - {report['airport']} ({report['status']})", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Mission Details**")
                        st.write(f"Airport: {report['airport']}")
                        st.write(f"Start Date: {report['date_start']}")
                        st.write(f"Completion Date: {report['date_finish']}")
                        st.write(f"Mission Status: {report['mission_status']}")
                        st.write(f"Review Status: {report['status']}")
                    
                    with col2:
                        st.write("**Team**")
                        st.write(f"Pilot: {report['pilote']}")
                        st.write(f"Data Analyst: {report['data_analyst']}")
                    
                    st.markdown("---")
                    st.write("**Findings**")
                    st.write(report['findings'])
                    
                    st.write("**Actions Taken**")
                    st.write(report['actions'])
                    
                    st.write("**Recommendations**")
                    st.write(report['recommendations'])
                    
                    # File download buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        if report['flight_profile']['name']:
                            st.download_button(
                                "Download Flight Profile",
                                data=report['flight_profile']['data'],
                                file_name=report['flight_profile']['name'],
                                key=f"reviewed_dl_profile_{report['ref']}"
                            )
                    with col2:
                        if report['report']['name']:
                            st.download_button(
                                "Download Mission Report",
                                data=report['report']['data'],
                                file_name=report['report']['name'],
                                key=f"reviewed_dl_report_{report['ref']}"
                            )
                    st.caption(f"Submitted: {report['timestamp']}")
    else:
        st.info("No completed mission reports available.")

# --- Mission Management ---
def chief_mission_management():
    st.subheader('Mission Management')
    if 'show_create_mission' not in st.session_state:
        st.session_state['show_create_mission'] = False
    if 'missions' not in st.session_state:
        st.session_state['missions'] = [
            {'ref': 'M001', 'airport': 'JFK', 'date_start': '2025-05-01', 'date_finish': '2025-05-03', 
             'duration': '2d', 'problem': 'Radar issue', 'status': 'En cours', 'assignment': 'New',
             'groupchief': 'houcine', 'pilote': 'ahmed', 'data_analyst': 'sara'},
            {'ref': 'M002', 'airport': 'LAX', 'date_start': '2025-04-20', 'date_finish': '2025-04-22', 
             'duration': '2d', 'problem': 'Comms check', 'status': 'Done', 'assignment': 'Accepted',
             'groupchief': 'hassan', 'pilote': 'jamal', 'data_analyst': 'salma'},
        ]
    
    if st.button('Create Mission', key='show_create_mission_btn'):
        st.session_state['show_create_mission'] = not st.session_state['show_create_mission']
    
    prefill = st.session_state.get('prefill_mission', {})
    if st.session_state['show_create_mission']:
        with st.form('create_mission_form', clear_on_submit=True):
            airport = st.text_input('Name of Airport', value=prefill.get('airport', ''))
            ref = st.text_input('Reference of the Mission', value=prefill.get('ref', ''))
            date_start = st.date_input('Date Start')
            date_finish = st.date_input('Date Finish')
            duration = st.text_input('Duration (auto-calc or manual)')
            problem = st.text_area('Problem to Fix', value=prefill.get('problem', ''))
            st.markdown('**Personnel Assignment**')
            groupchief = st.text_input('Group Chief')
            pilote = st.text_input('Pilote')
            data_analyst = st.text_input('Data Analyst')
            submitted = st.form_submit_button('Create Mission')
            if submitted:
                # Create new mission
                new_mission = {
                    'ref': ref,
                    'airport': airport,
                    'date_start': date_start.strftime('%Y-%m-%d'),
                    'date_finish': date_finish.strftime('%Y-%m-%d'),
                    'duration': duration,
                    'problem': problem,
                    'status': 'New',
                    'assignment': 'New',
                    'groupchief': groupchief,
                    'pilote': pilote,
                    'data_analyst': data_analyst
                }
                st.session_state['missions'].append(new_mission)
                st.success(f'Mission {ref} created!')
                st.info(f"Assigned: Group Chief: {groupchief}, Pilote: {pilote}, Data Analyst: {data_analyst}")
                if 'prefill_mission' in st.session_state:
                    del st.session_state['prefill_mission']
                st.session_state['show_create_mission'] = False
                # Add notification for ATSEP
                if 'atsep_notifications' not in st.session_state:
                    st.session_state['atsep_notifications'] = []
                st.session_state['atsep_notifications'].append({
                    'type': 'new_mission',
                    'mission_ref': ref,
                    'airport': airport,
                    'problem': problem,
                    'date': datetime.now().strftime('%Y-%m-%d')
                })
                st.rerun()
    
    # Display missions table
    st.markdown("### Current Missions")
    missions_df = st.data_editor(
        st.session_state['missions'],
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "status": st.column_config.SelectboxColumn(
                "Status",
                options=["New", "En cours", "Done"],
                required=True
            ),
            "assignment": st.column_config.SelectboxColumn(
                "Assignment",
                options=["New", "Accepted", "Rejected"],
                required=True
            )
        }
    )

# --- Drone Equipment Sub-Rubriques ---
def chief_drone_maintenance():
    st.markdown('## Maintenance History')
    st.caption('View all maintenance records submitted by ATSEP personnel')
    
    # Initialize shared maintenance records if not exists
    if 'shared_maintenance_records' not in st.session_state:
        st.session_state['shared_maintenance_records'] = [
            {'drone_id': 'D001', 'date': '2025-05-10', 'type': 'Calibration', 'desc': 'Annual calibration', 'tech': 'houcine', 'parts': '', 'timestamp': '2025-05-10 10:00:00'},
            {'drone_id': 'D002', 'date': '2025-04-15', 'type': 'Repair', 'desc': 'Motor replaced', 'tech': 'houcine', 'parts': 'Motor', 'timestamp': '2025-04-15 14:30:00'},
        ]
    
    maintenance_records = st.session_state['shared_maintenance_records']
    if not maintenance_records:
        st.info("No maintenance records available.")
    else:
        # Display records with details in expandable sections
        for record in sorted(maintenance_records, key=lambda x: x['timestamp'], reverse=True):
            with st.expander(f"{record['drone_id']} - {record['type']} ({record['date']})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Equipment:**", record['drone_id'])
                    st.write("**Maintenance Type:**", record['type'])
                    st.write("**Date:**", record['date'])
                with col2:
                    st.write("**Technician:**", record['tech'])
                    if record['parts']:
                        st.write("**Parts Changed:**", record['parts'])
                    st.write("**Added On:**", record['timestamp'])
                st.write("**Description:**", record['desc'])

def chief_drone_certificates():
    st.markdown('**Certificate Management**')
    if 'show_add_cert' not in st.session_state:
        st.session_state['show_add_cert'] = False
    if st.button('Add Certificate', key='show_add_cert_btn'):
        st.session_state['show_add_cert'] = not st.session_state['show_add_cert']
    
    if st.session_state['show_add_cert']:
        with st.form('add_cert_form', clear_on_submit=True):
            cert_name = st.text_input('Certificate Name')
            validation = st.text_input('Validation Duration')
            acq_date = st.date_input('Date Acquisition')
            exp_date = st.date_input('Date Fin Expiration')
            cert_file = st.file_uploader('Upload Calibration Certificate', type=['pdf', 'png', 'jpg'])
            submitted = st.form_submit_button('Add Certificate')
            if submitted and cert_file and cert_name:
                if 'certs' not in st.session_state:
                    st.session_state['certs'] = []
                st.session_state['certs'].append({'name': cert_name, 'validation': validation, 'acq': str(acq_date), 'exp': str(exp_date), 'file': cert_file.name, 'filedata': cert_file.getvalue()})
                st.success('Certificate added!')

    certs = st.session_state.get('certs', [
        {'name': 'Calib2025', 'validation': '1 year', 'acq': '2025-01-01', 'exp': '2026-01-01', 'file': 'calib2025.pdf', 'filedata': b'Sample certificate 2025'},
        {'name': 'Calib2024', 'validation': '1 year', 'acq': '2024-01-01', 'exp': '2025-01-01', 'file': 'calib2024.pdf', 'filedata': b'Sample certificate 2024'},
    ])
    
    # Display certificates for download above the table
    st.write("Download Certificates:")
    cert_cols = st.columns(len(certs))
    for idx, (col, cert) in enumerate(zip(cert_cols, certs)):
        with col:
            st.download_button(f"⬇️ {cert['file']}", 
                             data=cert['filedata'] if cert['filedata'] else b'Sample certificate', 
                             file_name=cert['file'],
                             key=f'dl_cert_{idx}')
    
    # Display the table without download buttons
    cert_rows = []
    for cert in certs:
        cert_rows.append({
            'Name': cert['name'],
            'Validation': cert['validation'],
            'Acquisition': cert['acq'],
            'Expiration': cert['exp'],
            'File': cert['file']
        })
    st.dataframe(cert_rows, use_container_width=True)

def chief_drone_location():
    st.markdown('**Drone Location Status**')
    
    # Get missions that are in progress
    missions = st.session_state.get('missions', [])
    active_missions = [m for m in missions if m['status'] == 'En cours']
    
    # Initialize drones with their status based on missions
    drones = []
    
    # Example drones - in real app you might want to load this from a configuration
    drone_ids = ['D001', 'D002', 'D003']
    
    for drone_id in drone_ids:
        # Find if drone is assigned to any active mission
        assigned_mission = next((m for m in active_missions if not any(d['drone_id'] == drone_id for d in drones)), None)
        
        if assigned_mission:
            drones.append({
                'drone_id': drone_id,
                'status': 'In Mission',
                'airport': assigned_mission['airport'],
                'duration': assigned_mission['duration'],
                'date_start': assigned_mission['date_start']
            })
        else:
            drones.append({
                'drone_id': drone_id,
                'status': 'Local Home',
                'airport': '',
                'duration': '',
                'date_start': ''
            })
            
    for d in drones:
        with st.expander(f"Drone {d['drone_id']} - {d['status']}"):
            if d['status'] == 'In Mission':
                st.write(f"Airport: {d['airport']}")
                st.write(f"Duration: {d['duration']}")
                st.write(f"Date Start: {d['date_start']}")
            else:
                st.write('Status: Local Home')

def chief_drone_spareparts():
    st.markdown('## Stock of Spare Parts')
    
    # Initialize spare parts in session state if not exists
    if 'spare_parts' not in st.session_state:
        st.session_state['spare_parts'] = [
            {'part_id': 'P001', 'name': 'Propeller', 'desc': 'Main propeller', 'qty': 10, 'min': 5},
            {'part_id': 'P002', 'name': 'Battery', 'desc': 'LiPo battery', 'qty': 3, 'min': 5},
        ]
    
    # Add new part button
    col1, col2 = st.columns([6,1])
    with col2:
        add_part = st.button("➕ Add Part", type="primary", use_container_width=True)
    
    if add_part:
        with st.form("add_part_form"):
            st.subheader("Add New Spare Part")
            
            col1, col2 = st.columns(2)
            with col1:
                part_id = st.text_input("Part ID", placeholder="e.g., P003")
                name = st.text_input("Part Name", placeholder="e.g., Motor")
                
            with col2:
                qty = st.number_input("Quantity", min_value=0, value=1)
                min_qty = st.number_input("Minimum Stock Level", min_value=0, value=5)
                
            desc = st.text_area("Description", placeholder="Part description...")
            
            submitted = st.form_submit_button("Add Part")
            if submitted:
                new_part = {
                    'part_id': part_id,
                    'name': name,
                    'desc': desc,
                    'qty': qty,
                    'min': min_qty
                }
                st.session_state['spare_parts'].append(new_part)
                st.success("Part added successfully!")
                st.rerun()
    
    # Display and edit spare parts
    parts = st.session_state['spare_parts']
    
    # Show warning for low stock items
    low_stock = [p for p in parts if p['qty'] <= p['min']]
    if low_stock:
        st.warning("⚠️ The following items are low in stock:")
        for p in low_stock:
            st.write(f"- {p['name']}: {p['qty']} remaining (minimum: {p['min']})")
    
    # Edit functionality
    st.markdown("### Current Stock")
    
    edited_parts = st.data_editor(
        parts,
        use_container_width=True,
        num_rows="dynamic",
        key="spare_parts_editor",
        column_config={
            "part_id": st.column_config.TextColumn("Part ID", help="Unique identifier for the part"),
            "name": st.column_config.TextColumn("Name", help="Name of the part"),
            "desc": st.column_config.TextColumn("Description", help="Part description"),
            "qty": st.column_config.NumberColumn("Quantity", help="Current quantity in stock", min_value=0),
            "min": st.column_config.NumberColumn("Min Stock", help="Minimum stock level", min_value=0)
        }
    )
    
    # Update session state if changes were made
    if edited_parts != st.session_state['spare_parts']:
        st.session_state['spare_parts'] = edited_parts
        st.success("Stock updated successfully!")
        
    # Use part functionality (for both Chief and ATSEP)
    st.markdown("### Use Parts")
    with st.form("use_parts_form"):
        col1, col2 = st.columns(2)
        with col1:
            part = st.selectbox("Select Part", options=[f"{p['name']} ({p['qty']} in stock)" for p in parts])
        with col2:
            use_qty = st.number_input("Quantity to Use", min_value=1, value=1)
            
        note = st.text_input("Usage Note", placeholder="Optional: Add a note about the usage")
        submitted = st.form_submit_button("Record Usage")
        
        if submitted:
            part_name = part.split(" (")[0]
            for p in st.session_state['spare_parts']:
                if p['name'] == part_name:
                    if p['qty'] >= use_qty:
                        p['qty'] -= use_qty
                        st.success(f"Used {use_qty} {part_name}(s). New stock level: {p['qty']}")
                        # Record usage in history if needed
                        if 'parts_usage_history' not in st.session_state:
                            st.session_state['parts_usage_history'] = []
                        st.session_state['parts_usage_history'].append({
                            'part_id': p['part_id'],
                            'name': p['name'],
                            'qty_used': use_qty,
                            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'user': st.session_state.get('username', 'Unknown'),
                            'note': note
                        })
                        st.rerun()
                    else:
                        st.error(f"Insufficient stock! Only {p['qty']} {part_name}(s) available.")
                    break

def chief_drone_equipment():
    st.subheader('Drone Equipment')
    sub = st.radio('Section', ['Maintenance History', 'Certificate Management', 'Drone Location', 'Spare Parts Management'])
    if sub == 'Maintenance History':
        chief_drone_maintenance()
    elif sub == 'Certificate Management':
        chief_drone_certificates()
    elif sub == 'Drone Location':
        chief_drone_location()
    elif sub == 'Spare Parts Management':
        chief_drone_spareparts()

# --- Downloads with Edit/Delete on Link Click ---
def chief_downloads():
    st.subheader('Downloads & Document Management')
    st.caption('Upload template documents and access files uploaded by ATSEP personnel for drone-based navaid maintenance operations.')
    # --- Upload Section ---
    st.markdown('### ⬆️ Upload Template Documents')
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('**Mission Templates & Forms**')
        mission_file = st.file_uploader('Upload Mission Template', type=['pdf', 'doc', 'docx', 'xls', 'xlsx'], key='mission_file')
        if st.button('Upload Mission Template') and mission_file:
            if 'downloads' not in st.session_state:
                st.session_state['downloads'] = []
            st.session_state['downloads'].append({'name': mission_file.name, 'content': mission_file.getvalue(), 'file': mission_file.name, 'type': 'Mission'})
            st.success('Mission template uploaded!')
            st.rerun()
        st.markdown('**Checklists & Procedures**')
        checklist_file = st.file_uploader('Upload Checklist', type=['pdf', 'doc', 'docx', 'xls', 'xlsx'], key='checklist_file')
        if st.button('Upload Checklist') and checklist_file:
            if 'downloads' not in st.session_state:
                st.session_state['downloads'] = []
            st.session_state['downloads'].append({'name': checklist_file.name, 'content': checklist_file.getvalue(), 'file': checklist_file.name, 'type': 'Checklist'})
            st.success('Checklist uploaded!')
            st.rerun()
    with col2:
        st.markdown('**Manuals & Documentation**')
        manual_file = st.file_uploader('Upload Manual/Guide', type=['pdf', 'doc', 'docx'], key='manual_file')
        if st.button('Upload Manual/Guide') and manual_file:
            if 'downloads' not in st.session_state:
                st.session_state['downloads'] = []
            st.session_state['downloads'].append({'name': manual_file.name, 'content': manual_file.getvalue(), 'file': manual_file.name, 'type': 'Manual'})
            st.success('Manual uploaded!')
            st.rerun()
        st.markdown('**General Documents**')
        general_file = st.file_uploader('Upload General Document', type=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png'], key='general_file')
        if st.button('Upload General Document') and general_file:
            if 'downloads' not in st.session_state:
                st.session_state['downloads'] = []
            st.session_state['downloads'].append({'name': general_file.name, 'content': general_file.getvalue(), 'file': general_file.name, 'type': 'General'})
            st.success('General document uploaded!')
            st.rerun()
    # --- Uploaded Section ---
    st.markdown('### 📂 Uploaded Template Documents')
    # Mission Templates & Forms
    st.markdown('#### Mission Templates & Forms')
    mission_files = [d for d in st.session_state.get('downloads', []) if d['type'] == 'Mission']
    for i, doc in enumerate(mission_files):
        with st.container():
            col1, col2 = st.columns([6,1])
            with col1:
                st.write(f"{doc['name']}")
            with col2:
                if st.download_button('Download', data=doc['content'], file_name=doc['file'], key=f'dl_mission_{i}'):
                    pass
                if st.button('Delete', key=f'del_mission_{i}'):
                    st.session_state['downloads'].remove(doc)
                    st.rerun()
    # Manuals & Documentation
    st.markdown('#### Manuals & Documentation')
    manual_files = [d for d in st.session_state.get('downloads', []) if d['type'] == 'Manual']
    for i, doc in enumerate(manual_files):
        with st.container():
            col1, col2 = st.columns([6,1])
            with col1:
                st.write(f"{doc['name']}")
            with col2:
                if st.download_button('Download', data=doc['content'], file_name=doc['file'], key=f'dl_manual_{i}'):
                    pass
                if st.button('Delete', key=f'del_manual_{i}'):
                    st.session_state['downloads'].remove(doc)
                    st.rerun()
    # Checklists & Procedures
    st.markdown('#### Checklists & Procedures')
    checklist_files = [d for d in st.session_state.get('downloads', []) if d['type'] == 'Checklist']
    for i, doc in enumerate(checklist_files):
        with st.container():
            col1, col2 = st.columns([6,1])
            with col1:
                st.write(f"{doc['name']}")
            with col2:
                if st.download_button('Download', data=doc['content'], file_name=doc['file'], key=f'dl_checklist_{i}'):
                    pass
                if st.button('Delete', key=f'del_checklist_{i}'):
                    st.session_state['downloads'].remove(doc)
                    st.rerun()
    # General Documents
    st.markdown('#### General Documents')
    general_files = [d for d in st.session_state.get('downloads', []) if d['type'] == 'General']
    for i, doc in enumerate(general_files):
        with st.container():
            col1, col2 = st.columns([6,1])
            with col1:
                st.write(f"{doc['name']}")
            with col2:
                if st.download_button('Download', data=doc['content'], file_name=doc['file'], key=f'dl_general_{i}'):
                    pass
                if st.button('Delete', key=f'del_general_{i}'):
                    st.session_state['downloads'].remove(doc)
                    st.rerun()

# --- Users Management ---
def chief_users_management():
    st.subheader('Users Management')
    
    # Initialize users in session state if not exists
    if 'users_list' not in st.session_state:
        st.session_state['users_list'] = [
            {'name': 'houcine fath', 'role': 'Group Chief', 'email': 'houcine@example.com', 'status': 'Active', 'username': 'houcine', 'password': 'chief123'},
            {'name': 'jamal Jon', 'role': 'Pilot', 'email': 'jam@example.com', 'status': 'Active', 'username': 'jamal', 'password': 'pilot123'},
            {'name': 'sara walo', 'role': 'Data Analyst', 'email': 'sara@example.com', 'status': 'Inactive', 'username': 'sara', 'password': 'analyst123'},
        ]
    
    # Add/Edit User Form at the top
    if st.session_state.get('show_add_user_form', False):
        with st.form("user_form"):
            edit_idx = st.session_state.get('edit_user')
            edit_user = st.session_state['users_list'][edit_idx] if edit_idx is not None else None
            
            st.write(f"### {'Edit' if edit_user else 'Add'} User")
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Full Name", value=edit_user['name'] if edit_user else '')
                email = st.text_input("Email", value=edit_user['email'] if edit_user else '')
                username = st.text_input("Username", value=edit_user.get('username', '') if edit_user else '')
            with col2:
                role = st.selectbox(
                    "Role", 
                    ["Group Chief", "Pilot", "Data Analyst"],
                    index=["Group Chief", "Pilot", "Data Analyst"].index(edit_user['role']) if edit_user else 0
                )
                status = st.selectbox(
                    "Status",
                    ["Active", "Inactive"],
                    index=["Active", "Inactive"].index(edit_user['status']) if edit_user else 0
                )
                password = st.text_input("Password", type="password", value=edit_user.get('password', '') if edit_user else '')
            
            col1, col2 = st.columns([1, 1])
            with col1:
                submitted = st.form_submit_button("Save User")
            with col2:
                if st.form_submit_button("Cancel"):
                    st.session_state['show_add_user_form'] = False
                    st.session_state['edit_user'] = None
                    st.rerun()
            
            if submitted:
                new_user = {
                    'name': name,
                    'email': email,
                    'role': role,
                    'status': status,
                    'username': username,
                    'password': password
                }
                
                if edit_idx is not None:
                    st.session_state['users_list'][edit_idx] = new_user
                    st.success(f"User {name} updated successfully!")
                else:
                    st.session_state['users_list'].append(new_user)
                    st.success(f"User {name} added successfully!")
                
                st.session_state['show_add_user_form'] = False
                st.session_state['edit_user'] = None
                st.rerun()
    
    # Search and Add User button
    search_container = st.container()
    col1, col2 = search_container.columns([3, 1])
    
    with col1:
        search = st.text_input("🔍 Search users...", key="user_search")
    
    with col2:
        if st.button("➕ Add User", key="add_user_btn"):
            st.session_state['show_add_user_form'] = True
            st.session_state['edit_user'] = None
            st.rerun()
    
    # Filter users based on search
    users = st.session_state['users_list']
    if search:
        users = [u for u in users if search.lower() in u['name'].lower() or 
                search.lower() in u['email'].lower() or 
                search.lower() in u.get('username', '').lower()]
    
    # Display users in expandable containers
    for idx, user in enumerate(users):
        with st.expander(f"{user['name']} - {user['role']}", expanded=False):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**Email:** {user['email']}")
                st.write(f"**Username:** {user.get('username', 'N/A')}")
                st.write(f"**Role:** {user['role']}")
                st.write(f"**Status:** {user['status']}")
            with col2:
                if st.button("✏️ Edit", key=f"edit_{idx}"):
                    st.session_state['show_add_user_form'] = True
                    st.session_state['edit_user'] = idx
                    st.rerun()
                if st.button("❌ Delete", key=f"delete_{idx}"):
                    st.session_state['users_list'].pop(idx)
                    st.success(f"User {user['name']} deleted successfully!")
                    st.rerun()

# --- Portal Problems ---
def chief_portal_problems():
    st.subheader('Portal Problems')
    
    # Get problems from session state or use empty list if none exist
    problems = st.session_state.get('problem_reports', [])
    
    # Show notification for new problems
    new_problems = [p for p in problems if p['status'] == 'New']
    if new_problems:
        st.warning(f"⚠️ You have {len(new_problems)} new problem report(s) that need attention!")
    
    # Filter controls
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.selectbox('Filter by Status', ['All', 'New', 'In Progress', 'Resolved'])
    with col2:
        airport_filter = st.text_input('Filter by Airport')
    
    # Filter problems
    filtered_problems = problems
    if status_filter != 'All':
        filtered_problems = [p for p in filtered_problems if p['status'] == status_filter]
    if airport_filter:
        filtered_problems = [p for p in filtered_problems if airport_filter.lower() in p['airport'].lower()]
    
    # Display problems in a table format with detailed view
    if filtered_problems:
        st.markdown("### Problem Reports")
        for problem in sorted(filtered_problems, key=lambda x: (x['priority'] == 'High', x['date']), reverse=True):
            with st.expander(
                f"🔴 {problem['airport']} - {problem['system']} (Priority: {problem['priority']}, Status: {problem['status']})",
                expanded=problem['status'] == 'New'
            ):
                col1, col2 = st.columns([2,1])
                with col1:
                    st.markdown("#### Problem Details")
                    st.write(f"**Problem Description:** {problem['description']}")
                    st.write(f"**Operational Impact:** {problem['impact']}")
                    if problem['additional_info']:
                        st.write(f"**Additional Information:** {problem['additional_info']}")
                with col2:
                    st.markdown("#### Report Information")
                    st.write(f"**Report ID:** {problem['id']}")
                    st.write(f"**Reporter:** {problem['reporter']}")
                    st.write(f"**Contact:** {problem['contact']}")
                    st.write(f"**Date Reported:** {problem['date']}")
                    st.write(f"**Priority Level:** {problem['priority']}")
                    
                # Status update section
                st.markdown("#### Update Status")
                new_status = st.selectbox(
                    "Update Status",
                    ['New', 'In Progress', 'Resolved'],
                    index=['New', 'In Progress', 'Resolved'].index(problem['status']),
                    key=f"status_{problem['id']}"
                )
                if new_status != problem['status']:
                    # Update the problem status in session state
                    for p in st.session_state['problem_reports']:
                        if p['id'] == problem['id']:
                            p['status'] = new_status
                            p['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            st.success(f"Status updated to {new_status}")
                            break
                
                st.caption(f"Last updated: {problem.get('last_updated', problem['timestamp'])}")
    else:
        st.info("No problem reports match your filter criteria.")

# --- ATSEP Interface ---

def atsep_dashboard():
    st.header('ATSEP Dashboard')
    st.caption('Manage your missions and maintenance tasks')
    
    # Get mission counts
    missions = st.session_state.get('missions', [])
    completed = sum(1 for m in missions if m['status'] == 'Done' and m['assignment'] == 'Accepted')
    in_progress = sum(1 for m in missions if m['status'] == 'En cours' and m['assignment'] == 'Accepted')
    new_assignments = sum(1 for m in missions if m['assignment'] == 'New')
    
    # Summary Cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True):
            st.markdown(f"### {completed}")
            st.markdown("#### ✓ Completed Missions")
            st.caption("Successfully completed")
            
    with col2:
        with st.container(border=True):
            st.markdown(f"### {in_progress}")
            st.markdown("#### 🕒 In Progress")
            st.caption("Currently working on")
            
    with col3:
        with st.container(border=True):
            st.markdown(f"### {new_assignments}")
            st.markdown("#### 🔔 New Assignments")
            st.caption("Waiting for acceptance")
    
    # Show notifications for new missions
    notifications = st.session_state.get('atsep_notifications', [])
    if notifications:
        st.markdown("## New Mission Notifications")
        for notif in notifications:
            if notif['type'] == 'new_mission':
                with st.container(border=True):
                    st.warning(f"🔔 New Mission Assignment!")
                    st.write(f"**Airport:** {notif['airport']}")
                    st.write(f"**Mission Reference:** {notif['mission_ref']}")
                    st.write(f"**Problem:** {notif['problem']}")
                    col1, col2 = st.columns([3,1])
                    with col2:
                        if st.button("Accept Mission", key=f"accept_{notif['mission_ref']}"):
                            # Update mission status
                            for mission in st.session_state['missions']:
                                if mission['ref'] == notif['mission_ref']:
                                    mission['assignment'] = 'Accepted'
                                    break
                            # Remove notification
                            st.session_state['atsep_notifications'].remove(notif)
                            st.success("Mission accepted!")
                            st.rerun()
                        if st.button("Reject", key=f"reject_{notif['mission_ref']}"):
                            # Update mission status
                            for mission in st.session_state['missions']:
                                if mission['ref'] == notif['mission_ref']:
                                    mission['assignment'] = 'Rejected'
                                    break
                            # Remove notification
                            st.session_state['atsep_notifications'].remove(notif)
                            st.rerun()
    
    # Mission History
    st.markdown("## Mission History")
    st.caption("History of your assigned maintenance missions")
    
    # Filter missions assigned to this ATSEP
    atsep_missions = [m for m in missions if m['assignment'] == 'Accepted']
    if not atsep_missions:
        st.info("No missions assigned yet. Check notifications for new assignments.")
    else:
        mission_data = []
        for mission in atsep_missions:
            mission_data.append({
                'Status': mission['status'],
                'Airport': mission['airport'],
                'Reference': mission['ref'],
                'Dates': f"{mission['date_start']} - {mission['date_finish']}",
                'Duration': mission['duration'],
                'Problem': mission['problem'],
                'Actions': '📋 View Details'
            })
        st.dataframe(
            mission_data,
            use_container_width=True,
            column_config={
                'Status': st.column_config.TextColumn(
                    'Status',
                    help='Current status of the mission'
                ),
                'Actions': st.column_config.TextColumn(
                    'Actions',
                    help='Available actions for this mission'
                )
            }
        )

def atsep_drone_maintenance():
    st.header('Drone Maintenance')
    
    # Initialize shared maintenance records in session state if not exists
    if 'shared_maintenance_records' not in st.session_state:
        st.session_state['shared_maintenance_records'] = [
            {'drone_id': 'D001', 'date': '2025-05-10', 'type': 'Calibration', 'desc': 'Annual calibration', 'tech': 'houcine', 'parts': '', 'timestamp': '2025-05-10 10:00:00'},
            {'drone_id': 'D002', 'date': '2025-04-15', 'type': 'Repair', 'desc': 'Motor replaced', 'tech': 'houcine', 'parts': 'Motor', 'timestamp': '2025-04-15 14:30:00'},
        ]
    
    # Add Maintenance Record button
    col1, col2 = st.columns([6,1])
    with col2:
        add_record = st.button("➕ Add Maintenance Record", type="primary", use_container_width=True)
    
    if add_record:
        with st.form("maintenance_form"):
            st.subheader("Add Maintenance Record")
            st.caption("Record maintenance performed on drone equipment")
            
            col1, col2 = st.columns(2)
            with col1:
                date = st.date_input("Date")
                equipment = st.text_input("Equipment", placeholder="e.g., DJI Matrice 300 RTK")
                
            with col2:
                maintenance_type = st.text_input("Maintenance Type", 
                                               placeholder="e.g., Regular inspection, Battery replacement")
                parts_changed = st.text_input("Parts Changed", 
                                            placeholder="e.g., Propellers, Battery pack (optional)")
            
            notes = st.text_area("Notes", placeholder="Detailed notes about the maintenance performed...")
            
            col1, col2 = st.columns([4,1])
            with col2:
                submitted = st.form_submit_button("Add Record", type="primary", use_container_width=True)
            
            if submitted:
                new_record = {
                    'drone_id': equipment,
                    'date': date.strftime('%Y-%m-%d'),
                    'type': maintenance_type,
                    'desc': notes,
                    'parts': parts_changed,
                    'tech': st.session_state.get('username', 'Unknown'),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                if 'shared_maintenance_records' not in st.session_state:
                    st.session_state['shared_maintenance_records'] = []
                st.session_state['shared_maintenance_records'].append(new_record)
                st.success("Maintenance record added successfully!")
                st.rerun()
    
    # Display maintenance records
    st.markdown("## Maintenance History")
    st.caption("Record of all maintenance activities performed on drone equipment")
    
    maintenance_records = st.session_state.get('shared_maintenance_records', [])
    if not maintenance_records:
        st.info("No maintenance records found. Add your first record above.")
    else:
        st.dataframe(
            sorted(maintenance_records, key=lambda x: x['timestamp'], reverse=True),
            use_container_width=True,
            column_config={
                'drone_id': st.column_config.TextColumn('Equipment'),
                'date': st.column_config.TextColumn('Date'),
                'type': st.column_config.TextColumn('Type'),
                'desc': st.column_config.TextColumn('Description'),
                'parts': st.column_config.TextColumn('Parts Changed'),
                'tech': st.column_config.TextColumn('Technician'),
                'timestamp': st.column_config.TextColumn('Added On')
            }
        )

def atsep_mission_reports():
    st.header('Mission Report')
    st.subheader('Submit Mission Report')
    st.caption('Complete the fields below to submit a report for a completed mission')
    
    # Get accepted missions for selection
    missions = [m for m in st.session_state.get('missions', []) 
               if m['assignment'] == 'Accepted' and m['status'] != 'Done']
    
    with st.form("mission_report_form"):
        # Mission Selection
        selected_mission = st.selectbox(
            "Select Mission",
            options=['Select a mission...'] + [m['ref'] for m in missions],
            key='mission_select'
        )
        
        # Auto-fill mission details if selected
        selected_data = next((m for m in missions if m['ref'] == selected_mission), None)
        
        col1, col2 = st.columns(2)
        with col1:
            airport = st.text_input("Airport", value=selected_data['airport'] if selected_data else '')
            start_date = st.date_input("Start Date")
            completion_date = st.date_input("Completion Date")
            
        with col2:
            status = st.selectbox("Status", ["Completed", "Partially Completed", "Need Follow-up"])
            pilot = st.text_input("Pilot Name")
            analyst = st.text_input("Data Analyst")
        
        findings = st.text_area("Findings", height=150)
        actions = st.text_area("Actions Taken", height=150)
        recommendations = st.text_area("Recommendations", height=150)
          # File Upload Section
        col1, col2 = st.columns(2)
        with col1:
            flight_profile = st.file_uploader("Upload Flight Profile", type=['pdf', 'doc', 'docx'])
            if flight_profile:
                st.success(f"Flight profile {flight_profile.name} ready for upload")
            
        with col2:
            mission_report_file = st.file_uploader("Upload Mission Report", type=['pdf', 'doc', 'docx'])
            if mission_report_file:
                st.success(f"Mission report {mission_report_file.name} ready for upload")
        
        submitted = st.form_submit_button("Submit Report", type="primary")
        if submitted and selected_mission != 'Select a mission...':
            # Create report data
            report_data = {
                'ref': selected_mission,
                'airport': airport,
                'date_start': start_date.strftime('%Y-%m-%d'),
                'date_finish': completion_date.strftime('%Y-%m-%d'),
                'status': 'Submitted',  # Set to Submitted for chief's notification
                'mission_status': status,  # Store the actual mission completion status
                'pilote': pilot,
                'data_analyst': analyst,
                'findings': findings,
                'actions': actions,
                'recommendations': recommendations,
                'flight_profile': {
                    'name': flight_profile.name if flight_profile else None,
                    'data': flight_profile.getvalue() if flight_profile else None
                },
                'report': {
                    'name': mission_report_file.name if mission_report_file else None,
                    'data': mission_report_file.getvalue() if mission_report_file else None
                },
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Store the report in session state
            if 'submitted_reports' not in st.session_state:
                st.session_state['submitted_reports'] = []
            st.session_state['submitted_reports'].append(report_data)
            
            # Update mission status
            for mission in st.session_state['missions']:
                if mission['ref'] == selected_mission:
                    mission['status'] = 'Done'
            
            # Clear the form
            st.success("Mission report submitted successfully!")
            st.rerun()
    
    # Display submitted reports
    if 'submitted_reports' in st.session_state and st.session_state['submitted_reports']:
        st.markdown("## Submitted Reports")
        for report in st.session_state['submitted_reports']:
            with st.expander(f"Report for Mission {report['ref']} - {report['airport']}"):
                st.write(f"**Status:** {report['status']}")
                st.write(f"**Date Range:** {report['date_start']} to {report['date_finish']}")
                st.write(f"**Team:** Pilot: {report['pilote']}, Analyst: {report['data_analyst']}")
                st.write("**Findings:**", report['findings'])
                st.write("**Actions Taken:**", report['actions'])
                st.write("**Recommendations:**", report['recommendations'])
                if report['flight_profile']['name']:
                    st.download_button(
                        "Download Flight Profile",
                        data=report['flight_profile']['data'],
                        file_name=report['flight_profile']['name'],
                        key=f"dl_profile_{report['ref']}"
                    )
                if report['report']['name']:
                    st.download_button(
                        "Download Mission Report",
                        data=report['report']['data'],
                        file_name=report['report']['name'],
                        key=f"dl_report_{report['ref']}"
                    )

# --- Maintenance Records ---
def maintenance_records():
    st.header('Maintenance Records')
    
    # Initialize maintenance records in session state if not exists
    if 'maintenance_records' not in st.session_state:
        st.session_state['maintenance_records'] = []
    
    # Add new maintenance record form
    with st.form("maintenance_record_form"):
        st.subheader('Add New Maintenance Record')
        
        col1, col2 = st.columns(2)
        with col1:
            equipment = st.text_input("Equipment/System")
            maintenance_type = st.selectbox(
                "Maintenance Type",
                ["Preventive", "Corrective", "Upgrade", "Inspection"]
            )
            maintenance_date = st.date_input("Maintenance Date")
            
        with col2:
            technician = st.text_input("Technician Name")
            status = st.selectbox(
                "Status",
                ["Completed", "In Progress", "Scheduled", "Postponed"]
            )
            next_maintenance = st.date_input("Next Maintenance Due")
        
        description = st.text_area("Description of Work")
        findings = st.text_area("Findings/Issues")
        actions = st.text_area("Actions Taken")
        
        submitted = st.form_submit_button("Submit Record")
        if submitted:
            record = {
                'id': len(st.session_state['maintenance_records']) + 1,
                'equipment': equipment,
                'type': maintenance_type,
                'date': maintenance_date.strftime('%Y-%m-%d'),
                'technician': technician,
                'status': status,
                'next_date': next_maintenance.strftime('%Y-%m-%d'),
                'description': description,
                'findings': findings,
                'actions': actions,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            st.session_state['maintenance_records'].append(record)
            st.success("Maintenance record added successfully!")
            st.rerun()
    
    # Display existing maintenance records
    if st.session_state['maintenance_records']:
        st.markdown("## Maintenance History")
        for record in sorted(
            st.session_state['maintenance_records'],
            key=lambda x: x['date'],
            reverse=True
        ):
            with st.expander(
                f"{record['equipment']} - {record['date']} ({record['status']})",
                expanded=False
            ):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Equipment/System:**", record['equipment'])
                    st.write("**Maintenance Type:**", record['type'])
                    st.write("**Date:**", record['date'])
                    st.write("**Status:**", record['status'])
                
                with col2:
                    st.write("**Technician:**", record['technician'])
                    st.write("**Next Maintenance:**", record['next_date'])
                    st.write("**Record ID:**", record['id'])
                
                st.markdown("---")
                st.write("**Description of Work:**", record['description'])
                st.write("**Findings/Issues:**", record['findings'])
                st.write("**Actions Taken:**", record['actions'])
                st.caption(f"Record created: {record['timestamp']}")
    else:
        st.info("No maintenance records available.")

# --- Client Problem Reports ---
def client_problem_reports():
    st.header('Problem Reports')
    
    # Initialize problem reports in session state if not exists
    if 'problem_reports' not in st.session_state:
        st.session_state['problem_reports'] = []
    
    # Add new problem report form
    with st.form("problem_report_form"):
        st.subheader('Submit New Problem Report')
        
        col1, col2 = st.columns(2)
        with col1:
            airport = st.text_input("Airport")
            system = st.text_input("System/Equipment Affected")
            priority = st.selectbox(
                "Priority Level",
                ["High", "Medium", "Low"]
            )
            
        with col2:
            reporter = st.text_input("Reporter Name")
            contact = st.text_input("Contact Information")
            report_date = st.date_input("Report Date")
        
        problem_description = st.text_area("Problem Description")
        impact = st.text_area("Operational Impact")
        additional_info = st.text_area("Additional Information", help="Any other relevant details")
        
        submitted = st.form_submit_button("Submit Report")
        if submitted:
            report = {
                'id': len(st.session_state['problem_reports']) + 1,
                'airport': airport,
                'system': system,
                'priority': priority,
                'reporter': reporter,
                'contact': contact,
                'date': report_date.strftime('%Y-%m-%d'),
                'description': problem_description,
                'impact': impact,
                'additional_info': additional_info,
                'status': 'New',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            st.session_state['problem_reports'].append(report)
            st.success("Problem report submitted successfully!")
            st.rerun()
    
    # Display existing problem reports
    if st.session_state['problem_reports']:
        st.markdown("## Submitted Problems")
        for report in sorted(
            st.session_state['problem_reports'],
            key=lambda x: (x['priority'] == 'High', x['date']),
            reverse=True
        ):
            with st.expander(
                f"{report['airport']} - {report['system']} ({report['priority']} Priority)",
                expanded=False
            ):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Airport:**", report['airport'])
                    st.write("**System:**", report['system'])
                    st.write("**Priority:**", report['priority'])
                    st.write("**Status:**", report['status'])
                
                with col2:
                    st.write("**Reporter:**", report['reporter'])
                    st.write("**Contact:**", report['contact'])
                    st.write("**Date:**", report['date'])
                    st.write("**Report ID:**", report['id'])
                
                st.markdown("---")
                st.write("**Problem Description:**", report['description'])
                st.write("**Operational Impact:**", report['impact'])
                if report['additional_info']:
                    st.write("**Additional Information:**", report['additional_info'])
                st.caption(f"Report submitted: {report['timestamp']}")
    else:
        st.info("No problem reports available.")

# --- Main App Logic ---
def main_app():
    app_header()
    role = st.session_state['role']
    
    if role == 'Chief of Unit':
        rubrique = st.sidebar.radio('Rubrique', [
            'Mission Tracking',
            'Mission Management',
            'Drone Equipment', 
            'Portal Problems',
            'Downloads',
            'Completed Missions Reports',
            'Users Management'
        ])
        
        if rubrique == 'Mission Tracking':
            chief_dashboard()
        elif rubrique == 'Mission Management':
            chief_mission_management()
        elif rubrique == 'Drone Equipment':
            chief_drone_equipment()
        elif rubrique == 'Portal Problems':
            chief_portal_problems()
        elif rubrique == 'Downloads':
            chief_downloads()
        elif rubrique == 'Completed Missions Reports':
            chief_completed_missions_reports()
        elif rubrique == 'Users Management':
            chief_users_management()
    
    elif role == 'ATSEP':
        rubrique = st.sidebar.radio('Navigation',
            ['My Missions', 'Drone Maintenance', 'Mission Reports'],
            key='atsep_nav'
        )
        
        if rubrique == 'My Missions':
            atsep_dashboard()
        elif rubrique == 'Drone Maintenance':
            atsep_drone_maintenance()
        elif rubrique == 'Mission Reports':
            atsep_mission_reports()
    
    elif role == 'Client':
        rubrique = st.sidebar.radio('Rubrique', [
            'Home',
            'Report Problem'
        ])
        
        if rubrique == 'Home':
            st.header('Client Home')
            st.subheader('Your Reported Problems')
            
            # Filter problems for current user
            user_problems = [p for p in st.session_state.get('problem_reports', []) 
                           if p['reporter'] == st.session_state.get('username')]
            
            if not user_problems:
                st.info('You have not reported any problems yet.')
            else:
                for problem in user_problems:
                    with st.expander(f"{problem['airport']} - {problem['system']} ({problem['date']})"):
                        st.write(f"**Priority:** {problem['priority']}")
                        st.write(f"**Problem Description:** {problem['description']}")
                        st.write(f"**Status:** {problem['status']}")
                        st.write(f"**Date Reported:** {problem['date']}")
                        if problem['additional_info']:
                            st.write(f"**Additional Info:** {problem['additional_info']}")
        elif rubrique == 'Report Problem':
            st.header('Report a Problem')
            client_problem_reports()

# --- App Entry Point ---
if 'authenticated' not in st.session_state or not st.session_state['authenticated']:
    login_form()
else:
    main_app()
