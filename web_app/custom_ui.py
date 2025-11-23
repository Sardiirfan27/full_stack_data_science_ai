import streamlit as st

def apply_modern_styles():
    """Apply modern styles by loading the CSS file"""
    # Styles are now loaded from style.css in app.py
    pass
def apply_global_styles():
    st.markdown("""
    <style>
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #1a1a1a;
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb {
        background: #4CAF50;
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #45a049;
    }

    /* Global Styles */
    .main-header {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        text-align: center;
        position: relative;
        overflow: hidden;
    }

    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(45deg, transparent 0%, rgba(255,255,255,0.1) 100%);
        z-index: 1;
    }

    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 600;
        margin: 0;
        position: relative;
        z-index: 2;
    }

    /* Template Card Styles */
    .template-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
        gap: 2rem;
        padding: 1rem;
    }

    .template-card {
        background: rgba(45, 45, 45, 0.9);
        border-radius: 20px;
        padding: 2rem;
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .template-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        border-color: #4CAF50;
    }

    .template-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(45deg, transparent 0%, rgba(76,175,80,0.1) 100%);
        z-index: 1;
    }

    .template-icon {
        font-size: 3rem;
        color: #4CAF50;
        margin-bottom: 1.5rem;
        position: relative;
        z-index: 2;
    }

    .template-title {
        font-size: 1.8rem;
        font-weight: 600;
        color: white;
        margin-bottom: 1rem;
        position: relative;
        z-index: 2;
    }

    .template-description {
        color: #aaa;
        margin-bottom: 1.5rem;
        position: relative;
        z-index: 2;
        line-height: 1.6;
    }

    /* Feature List Styles */
    .feature-list {
        list-style: none;
        padding: 0;
        margin: 1.5rem 0;
        position: relative;
        z-index: 2;
    }

    .feature-item {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
        color: #ddd;
        font-size: 0.95rem;
    }

    .feature-icon {
        color: #4CAF50;
        margin-right: 0.8rem;
        font-size: 1.1rem;
    }

    /* Button Styles */
    .action-button {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 50px;
        border: none;
        font-weight: 500;
        cursor: pointer;
        width: 100%;
        text-align: center;
        position: relative;
        overflow: hidden;
        z-index: 2;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .action-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(76,175,80,0.3);
    }

    .action-button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.2) 50%, transparent 100%);
        transition: all 0.6s ease;
    }

    .action-button:hover::before {
        left: 100%;
    }

    /* Form Section Styles */
    .form-section {
        background: rgba(45, 45, 45, 0.9);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
    }

    .form-section-title {
        font-size: 1.8rem;
        font-weight: 600;
        color: white;
        margin-bottom: 1.5rem;
        padding-bottom: 0.8rem;
        border-bottom: 2px solid #4CAF50;
    }

    .form-group {
        margin-bottom: 1.5rem;
    }

    .form-label {
        color: #ddd;
        font-weight: 500;
        margin-bottom: 0.8rem;
        display: block;
    }

    .form-input {
        width: 100%;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.1);
        background: rgba(30, 30, 30, 0.9);
        color: white;
        transition: all 0.3s ease;
    }

    .form-input:focus {
        border-color: #4CAF50;
        box-shadow: 0 0 0 2px rgba(76,175,80,0.2);
        outline: none;
    }

    /* Skill Tags */
    .skill-tag-container {
        display: flex;
        flex-wrap: wrap;
        gap: 0.8rem;
        margin-top: 1rem;
    }

    .skill-tag {
        background: rgba(76,175,80,0.1);
        color: #4CAF50;
        padding: 0.6rem 1.2rem;
        border-radius: 50px;
        border: 1px solid #4CAF50;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        cursor: pointer;
    }

    .skill-tag:hover {
        background: #4CAF50;
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(76,175,80,0.2);
    }

    /* Progress Circle */
    .progress-container {
        position: relative;
        width: 150px;
        height: 150px;
        margin: 2rem auto;
    }

    .progress-circle {
        transform: rotate(-90deg);
        width: 100%;
        height: 100%;
    }

    .progress-circle circle {
        fill: none;
        stroke-width: 8;
        stroke-linecap: round;
        stroke: #4CAF50;
        transform-origin: 50% 50%;
        transition: all 0.3s ease;
    }

    .progress-text {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 1.5rem;
        font-weight: 600;
        color: white;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .feature-card {
        background-color: #1e1e1e;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Animations */
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .animate-slide-in {
        animation: slideIn 0.6s cubic-bezier(0.4, 0, 0.2, 1) forwards;
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .template-container {
            grid-template-columns: 1fr;
        }

        .main-header {
            padding: 1.5rem;
        }

        .main-header h1 {
            font-size: 2rem;
        }

        .template-card {
            padding: 1.5rem;
        }

        .action-button {
            padding: 0.8rem 1.6rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)
        
def page_header(title, subtitle=None):
    """Render a consistent page header with gradient background"""
    st.markdown(
        f'''
        <div class="page-header">
            <h1 class="header-title">{title}</h1>
            {f'<p class="header-subtitle">{subtitle}</p>' if subtitle else ''}
        </div>
        ''',
        unsafe_allow_html=True
    )

def hero_section(title, subtitle=None, description=None):
    """Render a modern hero section with gradient background and animations"""
    # If description is provided but subtitle is not, use description as subtitle
    if description and not subtitle:
        subtitle = description
        description = None
    
    st.markdown(
        f'''
        <div class="page-header hero-header">
            <h1 class="header-title">{title}</h1>
            {f'<div class="header-subtitle">{subtitle}</div>' if subtitle else ''}
            {f'<p class="header-description">{description}</p>' if description else ''}
        </div>
        ''',
        unsafe_allow_html=True
    )

def feature_card(icon, title, description):
    """Render a modern feature card with hover effects"""
    st.markdown(f"""
        <div class="card feature-card">
            <div class="feature-icon icon-pulse">
                <i class="{icon}"></i>
            </div>
            <h3>{title}</h3>
            <p>{description}</p>
        </div>
    """, unsafe_allow_html=True)

def about_section(content, image_path=None, social_links=None):
    """Render a modern about section with profile image and social links"""
    st.markdown("""
        <div class="glass-card about-section">
            <div class="profile-section">
    """, unsafe_allow_html=True)
    
    # Profile Image
    if image_path:
        st.image(image_path, use_column_width=False, width=200)
    
    # Image Upload
    uploaded_file = st.file_uploader("Upload profile picture", type=['png', 'jpg', 'jpeg'])
    if uploaded_file is not None:
        st.image(uploaded_file, use_column_width=False, width=200)
    
    # Social Links
    if social_links:
        st.markdown('<div class="social-links">', unsafe_allow_html=True)
        for platform, url in social_links.items():
            st.markdown(f'<a href="{url}" target="_blank" class="social-link"><i class="fab fa-{platform.lower()}"></i></a>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # About Content
    st.markdown(f"""
            </div>
            <div class="about-content">{content}</div>
        </div>
    """, unsafe_allow_html=True)

def metric_card(label, value, delta=None, icon=None):
    """Render a modern metric card with animations"""
    icon_html = f'<i class="{icon}"></i>' if icon else ''
    delta_html = f'<div class="metric-delta">{delta}</div>' if delta else ''
    
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-header">
                {icon_html}
                <div class="metric-label">{label}</div>
            </div>
            <div class="metric-value">{value}</div>
            {delta_html}
        </div>
    """, unsafe_allow_html=True)

def template_card(title, description, image_url=None):
    """Render a modern template card with glassmorphism effect"""
    image_html = f'<img src="{image_url}" class="template-image" />' if image_url else ''
    
    st.markdown(f"""
        <div class="glass-card template-card">
            {image_html}
            <h3>{title}</h3>
            <p>{description}</p>
            <div class="card-overlay"></div>
        </div>
    """, unsafe_allow_html=True)

def feedback_card(name, feedback, rating):
    """Render a modern feedback card with rating stars"""
    stars = "⭐" * int(rating)
    
    st.markdown(f"""
        <div class="card feedback-card">
            <div class="feedback-header">
                <div class="feedback-name">{name}</div>
                <div class="feedback-rating">{stars}</div>
            </div>
            <p class="feedback-text">{feedback}</p>
        </div>
    """, unsafe_allow_html=True)

def loading_spinner(message="Loading..."):
    """Show a modern loading spinner with message"""
    st.markdown(f"""
        <div class="loading-container">
            <div class="loading-spinner"></div>
            <p class="loading-message">{message}</p>
        </div>
    """, unsafe_allow_html=True)

def progress_bar(value, max_value, label=None):
    """Render a modern animated progress bar"""
    percentage = (value / max_value) * 100
    label_html = f'<div class="progress-label">{label}</div>' if label else ''
    
    st.markdown(f"""
        <div class="progress-container">
            {label_html}
            <div class="progress-bar">
                <div class="progress-fill" style="width: {percentage}%"></div>
            </div>
            <div class="progress-value">{percentage:.1f}%</div>
        </div>
    """, unsafe_allow_html=True)

def tooltip(content, tooltip_text):
    """Render content with a modern tooltip"""
    st.markdown(f"""
        <div class="tooltip" data-tooltip="{tooltip_text}">
            {content}
        </div>
    """, unsafe_allow_html=True)

def data_table(data, headers):
    """Render a modern data table with hover effects"""
    header_row = "".join([f"<th>{header}</th>" for header in headers])
    rows = ""
    for row in data:
        cells = "".join([f"<td>{cell}</td>" for cell in row])
        rows += f"<tr>{cells}</tr>"
    
    st.markdown(f"""
        <div class="table-container">
            <table class="modern-table">
                <thead>
                    <tr>{header_row}</tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
    """, unsafe_allow_html=True)

def grid_layout(*elements):
    """Create a responsive grid layout"""
    st.markdown("""
        <div class="grid">
            {}
        </div>
    """.format("".join(elements)), unsafe_allow_html=True)

def alert(message, type="info"):
    """Display a modern alert message"""
    alert_types = {
        "info": ("ℹ️", "var(--accent-color)"),
        "success": ("✅", "var(--success-color)"),
        "warning": ("⚠️", "var(--warning-color)"),
        "error": ("❌", "var(--error-color)")
    }
    icon, color = alert_types.get(type, alert_types["info"])
    
    st.markdown(f"""
        <div class="alert alert-{type}">
            <span class="alert-icon">{icon}</span>
            <span class="alert-message">{message}</span>
        </div>
    """, unsafe_allow_html=True)

def about_section(title, description, team_members=None):
    st.markdown(f"""
        <div class="about-section">
            <h2>{title}</h2>
            <p class="about-description">{description}</p>
            {generate_team_section(team_members) if team_members else ''}
        </div>
        <style>
            .about-section {{
                background: linear-gradient(135deg, #2D2D2D 0%, #1E1E1E 100%);
                border-radius: 20px;
                padding: 3rem 2rem;
                margin: 2rem 0;
                position: relative;
                overflow: hidden;
            }}
            
            .about-section::before {{
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle, rgba(0,180,219,0.1) 0%, transparent 70%);
                animation: rotate 20s linear infinite;
            }}
            
            .about-section h2 {{
                color: #E0E0E0;
                margin-bottom: 1.5rem;
                font-size: 2rem;
            }}
            
            .about-description {{
                color: #B0B0B0;
                line-height: 1.6;
                font-size: 1.1rem;
                max-width: 800px;
                margin-bottom: 2rem;
            }}
            
            .team-section {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 1.5rem;
                margin-top: 2rem;
            }}
            
            .team-member {{
                background: #2D2D2D;
                border-radius: 15px;
                padding: 1.5rem;
                text-align: center;
                border: 1px solid #3D3D3D;
                transition: all 0.3s ease;
            }}
            
            .team-member:hover {{
                transform: translateY(-5px);
                border-color: #00B4DB;
            }}
            
            .team-member img {{
                width: 120px;
                height: 120px;
                border-radius: 50%;
                margin-bottom: 1rem;
            }}
            
            .team-member h3 {{
                color: #E0E0E0;
                margin-bottom: 0.5rem;
            }}
            
            .team-member p {{
                color: #B0B0B0;
            }}
        </style>
    """, unsafe_allow_html=True)

def generate_team_section(team_members):
    if not team_members:
        return ""
    
    team_html = '<div class="team-section">'
    for member in team_members:
        team_html += f"""
            <div class="team-member">
                <img src="{member['image']}" alt="{member['name']}">
                <h3>{member['name']}</h3>
                <p>{member['role']}</p>
            </div>
        """
    team_html += '</div>'
    return team_html

def render_feedback(feedback_data):
    """Render feedback with modern styling"""
    if not feedback_data:
        return
    
    feedback_html = """
    <div class="feedback-section">
        <h3 class="feedback-header">Resume Analysis Feedback</h3>
        <div class="feedback-content">
    """
    
    for category, items in feedback_data.items():
        if items:  # Only show categories with feedback
            for item in items:
                feedback_html += f"""
                <div class="feedback-item">
                    <div class="feedback-category">{category}</div>
                    <div class="feedback-description">{item}</div>
                </div>
                """
    
    feedback_html += """
        </div>
    </div>
    """
    
    st.markdown(feedback_html, unsafe_allow_html=True)

def render_analytics_section(resume_uploaded=False, metrics=None):
    """Render the analytics section of the dashboard"""
    if not metrics:
        metrics = {
            'views': 0,
            'downloads': 0,
            'score': 'N/A'
        }
    
    # Views Card
    st.markdown("""
        <div style='background: rgba(0, 20, 30, 0.3); border-radius: 15px; padding: 2rem; text-align: center; margin-bottom: 1rem;'>
            <div style='color: #00bfa5; font-size: 2.5rem; margin-bottom: 1rem;'>
                <i class='fas fa-eye'></i>
            </div>
            <h2 style='color: white; font-size: 1.5rem; margin-bottom: 1rem;'>Resume Views</h2>
            <p style='color: #00bfa5; font-size: 2.5rem; font-weight: bold; margin: 0;'>{}</p>
        </div>
    """.format(metrics['views']), unsafe_allow_html=True)
    
    # Downloads Card
    st.markdown("""
        <div style='background: rgba(0, 20, 30, 0.3); border-radius: 15px; padding: 2rem; text-align: center; margin-bottom: 1rem;'>
            <div style='color: #00bfa5; font-size: 2.5rem; margin-bottom: 1rem;'>
                <i class='fas fa-download'></i>
            </div>
            <h2 style='color: white; font-size: 1.5rem; margin-bottom: 1rem;'>Downloads</h2>
            <p style='color: #00bfa5; font-size: 2.5rem; font-weight: bold; margin: 0;'>{}</p>
        </div>
    """.format(metrics['downloads']), unsafe_allow_html=True)
    
    # Profile Score Card
    st.markdown("""
        <div style='background: rgba(0, 20, 30, 0.3); border-radius: 15px; padding: 2rem; text-align: center; margin-bottom: 1rem;'>
            <div style='color: #00bfa5; font-size: 2.5rem; margin-bottom: 1rem;'>
                <i class='fas fa-chart-line'></i>
            </div>
            <h2 style='color: white; font-size: 1.5rem; margin-bottom: 1rem;'>Profile Score</h2>
            <p style='color: #00bfa5; font-size: 2.5rem; font-weight: bold; margin: 0;'>{}</p>
        </div>
    """.format(metrics['score']), unsafe_allow_html=True)

def render_activity_section(resume_uploaded=False):
    """Render the recent activity section"""
    st.markdown("""
        <div style='background: rgba(0, 20, 30, 0.3); border-radius: 15px; padding: 2rem; height: 100%;'>
            <h2 style='color: white; font-size: 1.5rem; margin-bottom: 1.5rem;'>
                <i class='fas fa-history' style='color: #00bfa5; margin-right: 0.5rem;'></i> Recent Activity
            </h2>
    """, unsafe_allow_html=True)
    
    if resume_uploaded:
        st.markdown("""
            <div style='color: #ddd;'>
                <p style='margin: 0.8rem 0; font-size: 1.1rem;'>• Resume uploaded and analyzed</p>
                <p style='margin: 0.8rem 0; font-size: 1.1rem;'>• Generated optimization suggestions</p>
                <p style='margin: 0.8rem 0; font-size: 1.1rem;'>• Updated profile score</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style='text-align: center; padding: 2rem; color: #666;'>
                <i class='fas fa-upload' style='font-size: 2.5rem; color: #00bfa5; margin-bottom: 1rem;'></i>
                <p style='margin: 0; font-size: 1.1rem;'>Upload your resume to see activity</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_suggestions_section(resume_uploaded=False):
    """Render the suggestions section"""
    st.markdown("""
        <div style='background: rgba(0, 20, 30, 0.3); border-radius: 15px; padding: 2rem; height: 100%;'>
            <h2 style='color: white; font-size: 1.5rem; margin-bottom: 1.5rem;'>
                <i class='fas fa-lightbulb' style='color: #00bfa5; margin-right: 0.5rem;'></i> Suggestions
            </h2>
    """, unsafe_allow_html=True)
    
    if resume_uploaded:
        st.markdown("""
            <div style='color: #ddd;'>
                <p style='margin: 0.8rem 0; font-size: 1.1rem;'>• Add more quantifiable achievements</p>
                <p style='margin: 0.8rem 0; font-size: 1.1rem;'>• Include relevant keywords</p>
                <p style='margin: 0.8rem 0; font-size: 1.1rem;'>• Optimize formatting</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style='text-align: center; padding: 2rem; color: #666;'>
                <i class='fas fa-file-alt' style='font-size: 2.5rem; color: #00bfa5; margin-bottom: 1rem;'></i>
                <p style='margin: 0; font-size: 1.1rem;'>Upload your resume to get suggestions</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)