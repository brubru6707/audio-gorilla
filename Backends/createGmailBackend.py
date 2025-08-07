
import datetime
import copy
import uuid
import random
import json
from typing import Dict, Any
import json
current_datetime = datetime.datetime.now()

DEFAULT_STATE: Dict[str, Any] = {
    "users": {},
}
_user_email_to_uuid_map = {}

def generate_random_past_timestamp(max_days_ago=365):
    days_ago = random.randint(1, max_days_ago)
    return str(int((current_datetime - datetime.timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))).timestamp() * 1000))

def generate_future_timestamp(max_days_from_now=365):
    days_from_now = random.randint(1, max_days_from_now)
    return str(int((current_datetime + datetime.timedelta(days=days_from_now, hours=random.randint(0, 23), minutes=random.randint(0, 59))).timestamp() * 1000))

def generate_email(first_name, last_name):
    domains = ["example.com", "mail.net", "corp.org", "outlook.biz", "email.co"]
    return f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 99)}@{random.choice(domains)}"

def _create_user_data(email, first_name, last_name, recipients_emails, gmail_data):
    user_id = str(uuid.uuid4())
    _user_email_to_uuid_map[email] = user_id
    recipients_ids = recipients_emails
    processed_gmail_data = copy.deepcopy(gmail_data)
    new_messages = {}
    original_message_id_map = {}
    for msg_id_old, msg_data in processed_gmail_data.get("messages", {}).items():
        new_msg_id = str(uuid.uuid4())
        original_message_id_map[msg_id_old] = new_msg_id
        msg_data["id"] = new_msg_id
        msg_data["threadId"] = str(uuid.uuid4())
        if "internalDate" in msg_data and isinstance(msg_data["internalDate"], datetime.datetime):
            msg_data["internalDate"] = str(int(msg_data["internalDate"].timestamp() * 1000))
        elif "internalDate" not in msg_data:
            msg_data["internalDate"] = generate_random_past_timestamp()
        if "payload" not in msg_data:
            msg_data["payload"] = {"headers": []}
        if "headers" not in msg_data["payload"]:
            msg_data["payload"]["headers"] = []
        new_messages[new_msg_id] = msg_data
    processed_gmail_data["messages"] = new_messages
    final_threads = {}
    old_thread_to_new_thread_map = {}
    for msg_id_new, msg_data in processed_gmail_data["messages"].items():
        original_thread_id = None
        for old_thread_id, old_thread_data in gmail_data.get("threads", {}).items():
            if any(m.get("id") == msg_data.get("original_id") for m in old_thread_data.get("messages", [])):
                original_thread_id = old_thread_id
                break
        if original_thread_id:
            if original_thread_id not in old_thread_to_new_thread_map:
                old_thread_to_new_thread_map[original_thread_id] = str(uuid.uuid4())
            msg_data["threadId"] = old_thread_to_new_thread_map[original_thread_id]
        thread_id = msg_data["threadId"]
        if thread_id not in final_threads:
            final_threads[thread_id] = {"id": thread_id, "snippet": msg_data.get("snippet", "No snippet"), "messages": [], "historyId": str(random.randint(1000000000000, 9999999999999))}
        final_threads[thread_id]["messages"].append({"id": msg_id_new})
        current_snippet_ts = int(msg_data["internalDate"])
        thread_snippet_ts = int(final_threads[thread_id].get("snippet_timestamp", 0))
        if current_snippet_ts > thread_snippet_ts:
             final_threads[thread_id]["snippet"] = msg_data.get("snippet", "No snippet")
             final_threads[thread_id]["snippet_timestamp"] = current_snippet_ts
    processed_gmail_data["threads"] = final_threads
    new_drafts = {}
    for _, draft_data in processed_gmail_data.get("drafts", {}).items():
        new_draft_id = str(uuid.uuid4())
        draft_data["id"] = new_draft_id
        if "to" not in draft_data["message"]:
             draft_data["message"]["to"] = random.choice(["colleague@hostinger.com", "client@hostinger.net"])
        if "from" not in draft_data["message"]:
             draft_data["message"]["from"] = email
        new_drafts[new_draft_id] = draft_data
    processed_gmail_data["drafts"] = new_drafts
    new_labels = {}
    for _, label_data in processed_gmail_data.get("labels", {}).items():
        new_label_id = str(uuid.uuid4())
        label_data["id"] = new_label_id
        new_labels[new_label_id] = label_data
    processed_gmail_data["labels"] = new_labels
    default_system_labels = ["INBOX", "STARRED", "SPAM", "TRASH", "DRAFT", "SENT", "IMPORTANT", "UNREAD"]
    for sys_label in default_system_labels:
        if sys_label not in [lbl_data["name"] for lbl_data in processed_gmail_data["labels"].values()]:
            processed_gmail_data["labels"][str(uuid.uuid4())] = {
                "id": str(uuid.uuid4()),
                "name": sys_label,
                "messageListVisibility": "show",
                "labelListVisibility": "labelShow",
                "type": "system"
            }
    return user_id, {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "recipients": recipients_ids,
        "password_hash": uuid.uuid4().hex + ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=16)),
        "gmail_data": processed_gmail_data,
        "last_active": generate_random_past_timestamp(30),
        "timezone": random.choice(["America/New_York", "America/Los_Angeles", "Europe/London", "Asia/Tokyo"]),
    }

first_names = ["Sophia", "Liam", "Olivia", "Noah", "Ava", "Jackson", "Isabella", "Aiden", "Mia", "Lucas", "Harper", "Ethan", "Evelyn", "Mason", "Abigail", "Caleb", "Charlotte", "Logan", "Amelia", "Michael", "Ella", "Jacob", "Aria", "Daniel", "Chloe", "Samuel", "Grace", "David", "Victoria", "Joseph", "Penelope", "Matthew", "Riley", "Benjamin", "Layla", "Andrew", "Lily", "Gabriel", "Natalie", "Christopher", "Hannah", "James", "Zoe", "Ryan", "Scarlett", "Nathan", "Addison", "Christian", "Aubrey", "Joshua"]
last_names = ["Chen", "Kim", "Singh", "Lopez", "Garcia", "Nguyen", "Davis", "Jackson", "Harris", "White", "Moore", "Clark", "Lewis", "Baker", "Adams", "Hill", "Nelson", "Carter", "Mitchell", "Roberts", "Phillips", "Campbell", "Parker", "Evans", "Edwards", "Collins", "Stewart", "Morris", "Rogers", "Reed", "Cook", "Morgan", "Bell", "Murphy", "Bailey", "Rivera", "Cooper", "Richardson", "Cox", "Howard", "Ward", "Torres", "Peterson", "Gray", "Ramirez", "James", "Watson", "Brooks", "Kelly", "Sanders"]
first_names2 = ["Emma", "Oliver", "Sophia", "Liam", "Ava", "Noah", "Isabella", "Elijah", "Charlotte", "William", "Amelia", "James", "Mia", "Benjamin", "Harper"]
last_names2 = ["Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Taylor"]
email_subjects = [
    "Re: Project timeline update", "Follow up from yesterday's meeting", "Quick question about the proposal",
    "Meeting confirmation for tomorrow", "Document review needed", "Fwd: Important deadline reminder",
    "New client onboarding process", "Q4 planning session scheduled", "Budget approval request",
    "Team update and next steps", "Welcome to the team!", "Conference call rescheduled",
    "Action items from today's standup", "Proposal feedback requested", "Contract review - urgent",
    "Weekly status report", "Holiday schedule announcement", "Software update notification",
    "Client feedback summary", "Quarterly performance review", "Training session reminder",
    "Invoice processing update", "Vendor payment confirmation", "System maintenance window",
    "New product launch announcement", "Customer service escalation", "Marketing campaign results",
    "Sales target discussion", "HR policy update", "Office relocation notice",
    "Equipment request approval", "Travel expense reimbursement", "Conference attendance request",
    "Project milestone achieved", "Risk assessment findings", "Compliance audit results",
    "Partnership opportunity", "Merger announcement", "Stock option details",
    "Benefits enrollment reminder", "Performance bonus notification", "Promotion announcement",
    "Team building event", "Client presentation prep", "Board meeting agenda",
    "Shareholder update", "Acquisition discussion", "Due diligence request",
    "Legal review required", "Patent application status", "Trademark registration",
    "Quality assurance report", "Security breach notification", "Data backup verification",
    "Network upgrade schedule", "Software license renewal", "Hardware replacement plan",
    "Cloud migration timeline", "API integration update", "Database optimization",
    "User access permissions", "Password policy change", "Multi-factor authentication",
    "Cybersecurity training", "Phishing attempt alert", "Firewall configuration",
    "VPN setup instructions", "Remote work guidelines", "Laptop distribution",
    "Mobile device policy", "BYOD agreement", "IT support ticket",
    "Help desk response", "Technical documentation", "System requirements update",
    "Beta testing invitation", "Feature request discussion", "Bug report analysis",
    "Code review feedback", "Deployment schedule", "Release notes draft",
    "Version control update", "Repository access", "Development environment",
    "Testing framework", "Quality metrics", "Performance benchmarks",
    "Load testing results", "Security scan findings", "Penetration test report",
    "Vulnerability assessment", "Incident response plan", "Disaster recovery test",
    "Business continuity", "Emergency contact update", "Crisis communication",
    "Stakeholder meeting", "Investor relations", "Public relations strategy",
    "Media interview request", "Press release review", "Brand guidelines update",
    "Marketing collateral", "Website redesign", "SEO optimization",
    "Social media campaign", "Content calendar", "Blog post approval",
    "Newsletter template", "Email marketing metrics", "Customer segmentation",
    "Lead generation report", "Conversion rate analysis", "Sales funnel review",
    "Pipeline management", "CRM system update", "Customer onboarding",
    "Account management", "Renewal notification", "Upselling opportunity",
    "Cross-selling strategy", "Customer satisfaction", "Support ticket resolution",
    "Service level agreement", "Performance metrics", "KPI dashboard",
    "Analytics report", "Business intelligence", "Data visualization",
    "Market research findings", "Competitive analysis", "Industry trends",
    "Strategic planning", "SWOT analysis", "Risk mitigation",
    "Contingency planning", "Process improvement", "Workflow optimization",
    "Automation implementation", "Digital transformation", "Change management",
    "Employee engagement", "Talent acquisition", "Recruitment update",
    "Interview feedback", "Onboarding checklist", "Performance evaluation",
    "Career development", "Training completion", "Certification update",
    "Continuing education", "Professional development", "Conference summary",
    "Workshop attendance", "Seminar notes", "Webinar recording",
    "Knowledge sharing", "Best practices", "Lessons learned",
    "Project retrospective", "Sprint planning", "Agile methodology",
    "Scrum master update", "Product backlog", "User story refinement",
    "Acceptance criteria", "Definition of done", "Velocity tracking",
    "Burndown chart", "Capacity planning", "Resource allocation",
    "Team velocity", "Sprint review", "Daily standup notes",
    "Impediment removal", "Technical debt", "Code refactoring",
    "Architecture review", "Design pattern", "Framework selection",
    "Library evaluation", "Third-party integration", "Vendor assessment",
    "Procurement process", "Purchase order", "Contract negotiation",
    "Terms and conditions", "Service agreement", "Statement of work",
    "Project charter", "Scope definition", "Requirements gathering",
    "Functional specification", "Technical specification", "System design",
    "Interface definition", "Data model", "Schema update",
    "Migration plan", "Rollback procedure", "Deployment checklist",
    "Go-live preparation", "User acceptance testing", "Integration testing",
    "Regression testing", "Performance testing", "Stress testing",
    "Usability testing", "Accessibility compliance", "Localization update",
    "Translation review", "Cultural adaptation", "Regional requirements",
    "Regulatory compliance", "Audit preparation", "Documentation review",
    "Policy enforcement", "Procedure update", "Standard operating procedure",
    "Work instruction", "Training manual", "User guide",
    "Installation guide", "Configuration manual", "Troubleshooting guide",
    "FAQ update", "Knowledge base", "Support documentation",
    "Customer portal", "Self-service options", "Ticket automation",
    "Response time improvement", "First contact resolution", "Customer feedback",
    "Survey results", "Net promoter score", "Customer lifetime value",
    "Churn analysis", "Retention strategy", "Win-back campaign",
    "Loyalty program", "Rewards system", "Points redemption",
    "Gift card promotion", "Discount code", "Special offer",
    "Flash sale announcement", "Inventory clearance", "New arrival notification",
    "Back in stock alert", "Price adjustment", "Shipping update",
    "Delivery confirmation", "Return authorization", "Exchange request",
    "Refund processing", "Warranty claim", "Product recall",
    "Safety notice", "Maintenance schedule", "Inspection report",
    "Calibration certificate", "Quality control", "Manufacturing update",
    "Supply chain disruption", "Supplier notification", "Vendor performance",
    "Cost reduction initiative", "Profit margin analysis", "Revenue forecast",
    "Financial planning", "Budget revision", "Expense tracking",
    "Cash flow projection", "Investment opportunity", "Funding request"
]
email_bodies = [
    "Hi there,\n\nI wanted to follow up on our conversation from yesterday. Could we schedule a quick call to discuss the next steps?\n\nBest regards,\n{sender_name}",
    "Hello,\n\nI'm writing to confirm our meeting scheduled for tomorrow at 2 PM. Please let me know if you need to reschedule.\n\nThanks,\n{sender_first}",
    "Hi team,\n\nI've attached the updated project timeline for your review. Please take a look and let me know if you have any questions or concerns.\n\nRegards,\n{sender_name}",
    "Dear {recipient_type},\n\nI hope this email finds you well. I wanted to touch base regarding the proposal we discussed last week. When would be a good time to connect?\n\nBest,\n{sender_first}",
    "Hi,\n\nJust a quick reminder about the deadline coming up on Friday. Please make sure to submit your materials by end of day.\n\nThanks for your attention to this.\n\n{sender_name}",
    "Hello,\n\nI reviewed the documents you sent over and have a few questions. Would you be available for a brief call this afternoon to clarify a few points?\n\nLooking forward to hearing from you,\n{sender_first}",
    "Hi there,\n\nThank you for your interest in our services. I'd like to set up a time to discuss how we can help with your upcoming project. Are you available next week for a consultation?\n\nBest regards,\n{sender_name}",
    "Dear team,\n\nI wanted to share an update on the current status of our initiative. We're making good progress and should be on track to meet our Q4 goals.\n\nI'll send more details in a separate email.\n\n{sender_first}",
    "Good morning,\n\nI hope you had a great weekend. I wanted to circle back on the proposal we discussed and see if you've had a chance to review the terms.\n\nPlease let me know your thoughts.\n\nBest,\n{sender_name}",
    "Hi,\n\nI'm reaching out to introduce myself as your new point of contact for this project. I look forward to working with you and will be in touch soon with next steps.\n\nWarm regards,\n{sender_first}",
    "Hello everyone,\n\nI wanted to provide a quick update on our quarterly results. Overall, we've exceeded expectations and are well-positioned for the next quarter.\n\nDetailed report attached.\n\n{sender_name}",
    "Dear {recipient_type},\n\nThank you for taking the time to meet with me last week. I've compiled the action items we discussed and wanted to confirm the timeline.\n\nPlease review and let me know if I missed anything.\n\nBest regards,\n{sender_first}",
    "Hi team,\n\nI hope everyone is doing well. I wanted to remind you about our upcoming training session scheduled for next Thursday at 10 AM.\n\nPlease confirm your attendance.\n\nThanks,\n{sender_name}",
    "Good afternoon,\n\nI'm writing to request approval for the budget increase we discussed in yesterday's meeting. The additional funds will help us meet our delivery timeline.\n\nPlease let me know if you need any additional information.\n\n{sender_first}",
    "Hello,\n\nI wanted to follow up on the customer feedback we received and discuss potential improvements to our service delivery.\n\nCould we schedule a brief call this week?\n\nBest,\n{sender_name}",
    "Hi there,\n\nI hope you're doing well. I wanted to share some exciting news about our new product launch and get your thoughts on the marketing strategy.\n\nLooking forward to your feedback.\n\n{sender_first}",
    "Dear team,\n\nI'm pleased to announce that we've successfully completed the first phase of our digital transformation initiative. Thank you all for your hard work.\n\nNext steps will be communicated shortly.\n\n{sender_name}",
    "Good morning,\n\nI wanted to check in on the progress of the integration project. Are we still on track for the planned go-live date?\n\nPlease update me on any potential risks or blockers.\n\nThanks,\n{sender_first}",
    "Hello,\n\nI'm writing to confirm the details of our upcoming conference call. The agenda includes budget review, timeline updates, and resource allocation.\n\nCall details attached.\n\nBest regards,\n{sender_name}",
    "Hi everyone,\n\nI wanted to share the results of our recent customer satisfaction survey. The feedback has been overwhelmingly positive.\n\nFull report available in the shared folder.\n\n{sender_first}",
    "Dear {recipient_type},\n\nI hope this message finds you well. I'm reaching out to discuss the partnership opportunity we briefly touched on last month.\n\nWould you be available for a more detailed conversation?\n\nBest,\n{sender_name}",
    "Good afternoon,\n\nI wanted to provide an update on the security audit we recently completed. Overall, our systems are performing well with only minor recommendations.\n\nDetailed findings attached.\n\n{sender_first}",
    "Hello team,\n\nI'm excited to announce that we've been selected as a finalist for the industry innovation award. This recognition reflects all of our hard work.\n\nCelebration details to follow.\n\n{sender_name}",
    "Hi,\n\nI wanted to follow up on our discussion about the new hire onboarding process. I've prepared some recommendations for streamlining the workflow.\n\nPlease review when you have a chance.\n\nThanks,\n{sender_first}",
    "Dear all,\n\nI'm writing to inform you about the upcoming system maintenance window scheduled for this weekend. Services will be temporarily unavailable.\n\nPlease plan accordingly.\n\nBest regards,\n{sender_name}",
    "Good morning,\n\nI hope your week is off to a great start. I wanted to discuss the feedback we received from the client presentation yesterday.\n\nOverall response was very positive.\n\n{sender_first}",
    "Hello,\n\nI'm reaching out to schedule our monthly review meeting. I'd like to discuss progress on key initiatives and address any concerns.\n\nPlease let me know your availability.\n\nBest,\n{sender_name}",
    "Hi team,\n\nI wanted to share some updates on our competitive analysis. We're maintaining our market position despite increased competition.\n\nFull analysis in the attached document.\n\n{sender_first}",
    "Dear {recipient_type},\n\nThank you for your continued partnership. I wanted to discuss renewal terms for the upcoming contract period.\n\nI'll send over the preliminary terms shortly.\n\nBest regards,\n{sender_name}",
    "Good afternoon,\n\nI hope you're having a productive day. I wanted to check on the status of the vendor evaluation process.\n\nAny updates to share?\n\nThanks,\n{sender_first}",
    "Hello everyone,\n\nI'm pleased to report that we've successfully implemented the new quality control measures. Early results show significant improvement.\n\nDetailed metrics available upon request.\n\n{sender_name}",
    "Hi,\n\nI wanted to follow up on the training session from last week. Please let me know if you have any additional questions or need clarification on any topics.\n\nAlways happy to help.\n\n{sender_first}",
    "Dear team,\n\nI'm writing to announce some exciting changes to our organizational structure that will help us better serve our clients.\n\nDetails will be shared in tomorrow's all-hands meeting.\n\n{sender_name}",
    "Good morning,\n\nI hope you had a restful weekend. I wanted to discuss the resource allocation for the upcoming quarter.\n\nCould we schedule time this week?\n\nBest,\n{sender_first}",
    "Hello,\n\nI'm reaching out regarding the compliance audit scheduled for next month. We need to prepare the necessary documentation.\n\nI'll coordinate with all relevant departments.\n\nThanks,\n{sender_name}",
    "Hi there,\n\nI wanted to share the positive feedback we received from our latest client delivery. The team's hard work really paid off.\n\nKeep up the excellent work!\n\n{sender_first}",
    "Dear all,\n\nI'm writing to inform you about the new employee benefits package that will take effect next quarter.\n\nDetailed information will be distributed shortly.\n\nBest regards,\n{sender_name}",
    "Good afternoon,\n\nI hope your day is going well. I wanted to discuss the preliminary results from our market research study.\n\nVery encouraging findings to share.\n\n{sender_first}",
    "Hello team,\n\nI wanted to provide an update on our sustainability initiative. We're making excellent progress toward our environmental goals.\n\nQuarterly report attached.\n\n{sender_name}",
    "Hi,\n\nI'm following up on the action items from our strategy session. Most deliverables are on track, but a few need attention.\n\nLet's prioritize accordingly.\n\nThanks,\n{sender_first}",
    "Dear {recipient_type},\n\nI hope this email finds you in good health. I wanted to discuss the potential for expanding our collaboration.\n\nI believe there are mutual benefits to explore.\n\nBest,\n{sender_name}",
    "Good morning,\n\nI wanted to share an update on our customer retention efforts. The new program is showing promising early results.\n\nDetailed analysis in progress.\n\n{sender_first}",
    "Hello,\n\nI'm writing to confirm the logistics for our upcoming conference presentation. Everything appears to be on track.\n\nFinal details will be confirmed by Friday.\n\nBest regards,\n{sender_name}",
    "Hi everyone,\n\nI wanted to announce that we've received industry certification for our quality management system. This is a significant achievement.\n\nCongratulations to the entire team!\n\n{sender_first}",
    "Dear team,\n\nI'm pleased to report that our latest product release has been well-received by customers. Sales are exceeding projections.\n\nGreat work by everyone involved.\n\n{sender_name}",
    "Good afternoon,\n\nI hope you're having a productive week. I wanted to discuss the timeline for the upcoming system upgrade.\n\nPlanning meeting scheduled for tomorrow.\n\n{sender_first}",
    "Hello,\n\nI'm reaching out to gather feedback on the new workflow process we implemented last month. Your input is valuable for continuous improvement.\n\nPlease share your thoughts.\n\nThanks,\n{sender_name}",
    "Hi there,\n\nI wanted to follow up on the partnership discussion we had at the conference. I believe there's strong potential for collaboration.\n\nWould you be open to a follow-up call?\n\n{sender_first}",
    "Dear all,\n\nI'm writing to inform you about the upcoming holiday schedule and office closure dates. Please plan your projects accordingly.\n\nDetailed schedule attached.\n\nBest regards,\n{sender_name}",
    "Good morning,\n\nI hope your week is starting well. I wanted to share the results of our employee satisfaction survey.\n\nOverall scores have improved significantly.\n\n{sender_first}",
    "Hello team,\n\nI wanted to provide an update on our cost reduction initiative. We're ahead of target and seeing positive results.\n\nThanks for everyone's cooperation.\n\n{sender_name}",
    "Hi,\n\nI'm following up on the budget proposal we submitted last week. Do you need any additional information to complete the review?\n\nPlease let me know.\n\nThanks,\n{sender_first}",
    "Dear {recipient_type},\n\nI hope you're doing well. I wanted to discuss the feedback from our recent client meeting.\n\nOverall, the response was very positive.\n\nBest,\n{sender_name}",
    "Good afternoon,\n\nI wanted to share an update on our recruitment efforts. We've identified several strong candidates for the open positions.\n\nInterview schedule being finalized.\n\n{sender_first}",
    "Hello,\n\nI'm writing to confirm the agenda for our quarterly business review. All departments have submitted their reports.\n\nMeeting materials will be distributed tomorrow.\n\nBest regards,\n{sender_name}",
    "Hi everyone,\n\nI wanted to announce the launch of our new customer portal. This will significantly improve the user experience.\n\nTraining sessions will be scheduled soon.\n\n{sender_first}",
    "Dear team,\n\nI'm pleased to share that we've successfully completed the merger integration. All systems are now unified.\n\nThank you for your patience during the transition.\n\n{sender_name}",
    "Good morning,\n\nI hope you had a great weekend. I wanted to discuss the performance metrics from last quarter.\n\nScheduling individual review meetings this week.\n\n{sender_first}",
    "Hello,\n\nI'm reaching out regarding the intellectual property review we discussed. Legal has completed their analysis.\n\nRecommendations will be shared shortly.\n\nThanks,\n{sender_name}",
    "Hi there,\n\nI wanted to follow up on the customer service improvements we've been implementing. Early feedback is very encouraging.\n\nDetailed report next week.\n\n{sender_first}",
    "Dear all,\n\nI'm writing to announce the winners of our innovation challenge. The submitted ideas were truly impressive.\n\nAward ceremony scheduled for Friday.\n\nBest regards,\n{sender_name}",
    "Good afternoon,\n\nI hope your day is going smoothly. I wanted to discuss the preliminary budget allocations for next fiscal year.\n\nPlanning session tomorrow at 2 PM.\n\n{sender_first}",
    "Hello team,\n\nI wanted to share the results of our latest security assessment. Our defenses are strong, with only minor recommendations.\n\nFull report available in the secure folder.\n\n{sender_name}",
    "Hi,\n\nI'm following up on the vendor contract negotiations. We're making good progress on the key terms.\n\nExpect final agreement next week.\n\nThanks,\n{sender_first}",
    "Dear {recipient_type},\n\nI hope this message finds you well. I wanted to discuss the strategic partnership opportunity we briefly mentioned.\n\nWould you be interested in exploring this further?\n\nBest,\n{sender_name}",
    "Good morning,\n\nI wanted to provide an update on our digital marketing campaign. The engagement metrics are exceeding expectations.\n\nDetailed analytics report attached.\n\n{sender_first}",
    "Hello,\n\nI'm writing to confirm the details of our upcoming product demonstration. All technical requirements have been verified.\n\nLooking forward to a successful presentation.\n\nBest regards,\n{sender_name}",
    "Hi everyone,\n\nI wanted to announce that we've achieved our diversity and inclusion goals ahead of schedule. This is a team effort.\n\nCelebration event details to follow.\n\n{sender_first}",
    "Dear team,\n\nI'm pleased to report that our customer acquisition costs have decreased while retention rates have improved.\n\nExcellent work by the entire organization.\n\n{sender_name}",
    "Good afternoon,\n\nI hope you're having a productive day. I wanted to discuss the resource requirements for the upcoming project phase.\n\nTeam meeting scheduled for tomorrow.\n\n{sender_first}",
    "Hello,\n\nI'm reaching out to gather input on the proposed changes to our remote work policy. Your feedback is important.\n\nSurvey link will be sent shortly.\n\nThanks,\n{sender_name}",
    "Hi there,\n\nI wanted to follow up on the training program evaluation. Participant feedback has been overwhelmingly positive.\n\nProgram expansion under consideration.\n\n{sender_first}",
    "Dear all,\n\nI'm writing to inform you about the new data privacy regulations that will affect our operations.\n\nCompliance training will be mandatory.\n\nBest regards,\n{sender_name}",
    "Good morning,\n\nI hope your week is off to a strong start. I wanted to share the preliminary results from our market expansion study.\n\nVery promising opportunities identified.\n\n{sender_first}",
    "Hello team,\n\nI wanted to provide an update on our environmental sustainability efforts. We're on track to meet all our targets.\n\nProgress report attached for review.\n\n{sender_name}",
    "Hi,\n\nI'm following up on the equipment upgrade proposal we discussed. IT has completed their technical evaluation.\n\nRecommendations will be presented Friday.\n\nThanks,\n{sender_first}",
    "Dear {recipient_type},\n\nI hope you're doing well. I wanted to discuss the potential for a joint venture in the emerging markets.\n\nInitial feasibility looks promising.\n\nBest,\n{sender_name}",
    "Good afternoon,\n\nI wanted to share the customer testimonials we've received for our latest service offering. The feedback is exceptional.\n\nMarketing will feature these prominently.\n\n{sender_first}",
    "Hello,\n\nI'm writing to confirm the logistics for our annual conference. Registration is ahead of last year's numbers.\n\nFinal preparations are underway.\n\nBest regards,\n{sender_name}",
    "Hi everyone,\n\nI wanted to announce that we've been recognized as an industry leader in innovation. This reflects our commitment to excellence.\n\nPress release will be distributed tomorrow.\n\n{sender_first}",
    "Dear team,\n\nI'm pleased to share that our operational efficiency improvements are delivering the expected results.\n\nCost savings are ahead of projections.\n\n{sender_name}",
    "Good morning,\n\nI hope you had a restful weekend. I wanted to discuss the feedback from our recent board presentation.\n\nBoard members were very impressed.\n\n{sender_first}",
    "Hello,\n\nI'm reaching out regarding the succession planning initiative we discussed. HR has developed a comprehensive framework.\n\nReview meeting scheduled for next week.\n\nThanks,\n{sender_name}",
    "Hi there,\n\nI wanted to follow up on the competitive intelligence report. The insights will help shape our strategy.\n\nExecutive summary attached.\n\n{sender_first}",
    "Dear all,\n\nI'm writing to announce the expansion of our global operations. New offices will open in three key markets.\n\nDetailed timeline will be shared soon.\n\nBest regards,\n{sender_name}",
    "Good afternoon,\n\nI hope your day is productive. I wanted to discuss the performance improvement plan we've developed.\n\nImplementation begins next quarter.\n\n{sender_first}",
    "Hello team,\n\nI wanted to share the results of our recent employee engagement survey. Scores have improved across all categories.\n\nThanks for your continued dedication.\n\n{sender_name}",
    "Hi,\n\nI'm following up on the risk assessment we completed last month. The mitigation strategies are being implemented.\n\nProgress update meeting tomorrow.\n\nThanks,\n{sender_first}",
    "Dear {recipient_type},\n\nI hope this email finds you well. I wanted to discuss the licensing agreement renewal that's coming up.\n\nNegotiations should begin soon.\n\nBest,\n{sender_name}",
    "Good morning,\n\nI wanted to provide an update on our artificial intelligence initiative. The pilot program is showing excellent results.\n\nFull rollout planned for next year.\n\n{sender_first}",
    "Hello,\n\nI'm writing to confirm the details of our upcoming audit. All required documentation has been prepared.\n\nAuditors will begin their review Monday.\n\nBest regards,\n{sender_name}",
    "Hi everyone,\n\nI wanted to announce that we've achieved record sales for the quarter. This is a testament to everyone's hard work.\n\nBonus information will be communicated separately.\n\n{sender_first}",
    "Dear team,\n\nI'm pleased to report that our new product development timeline is ahead of schedule. Launch preparations are beginning.\n\nMarketing campaign strategy meeting Friday.\n\n{sender_name}",
    "Good afternoon,\n\nI hope you're having a great week. I wanted to discuss the feedback from our recent customer focus groups.\n\nInsights are very valuable for product development.\n\n{sender_first}",
    "Hello,\n\nI'm reaching out to discuss the proposed changes to our organizational structure. The benefits analysis is complete.\n\nImplementation timeline under review.\n\nThanks,\n{sender_name}",
    "Hi there,\n\nI wanted to follow up on the professional development opportunities we discussed. Several excellent programs are available.\n\nEnrollment deadline is next Friday.\n\n{sender_first}",
    "Dear all,\n\nI'm writing to inform you about the new cybersecurity protocols that will be implemented. Training is mandatory.\n\nSchedule will be distributed tomorrow.\n\nBest regards,\n{sender_name}",
    "Good morning,\n\nI hope your day is starting well. I wanted to share the results of our latest market research study.\n\nStrategic implications are significant.\n\n{sender_first}",
    "Hello team,\n\nI wanted to provide an update on our community outreach program. We've exceeded our volunteer hour goals.\n\nThank you for your participation.\n\n{sender_name}",
    "Hi,\n\nI'm following up on the supplier diversity initiative we launched. Early results are very encouraging.\n\nQuarterly report will be available soon.\n\nThanks,\n{sender_first}",
    "Dear {recipient_type},\n\nI hope you're doing well. I wanted to discuss the joint research project proposal we submitted.\n\nFunding decision expected next month.\n\nBest,\n{sender_name}",
    "Good afternoon,\n\nI wanted to share the customer satisfaction scores from our latest survey. Ratings have improved significantly.\n\nService team deserves recognition.\n\n{sender_first}",
    "Hello,\n\nI'm writing to confirm the agenda for our strategic planning retreat. All department heads have confirmed attendance.\n\nMaterials will be distributed Friday.\n\nBest regards,\n{sender_name}",
    "Hi everyone,\n\nI wanted to announce that we've received approval for the new research and development facility. Construction begins soon.\n\nThis will significantly expand our capabilities.\n\n{sender_first}",
    "Dear team,\n\nI'm pleased to share that our patent application has been approved. This protects our intellectual property.\n\nLegal will handle the implementation details.\n\n{sender_name}",
    "Good morning,\n\nI hope you had a wonderful weekend. I wanted to discuss the performance metrics dashboard we've developed.\n\nReal-time visibility into key indicators.\n\n{sender_first}",
    "Hello,\n\nI'm reaching out regarding the mentorship program we discussed. Interest has been overwhelming.\n\nMatching process will begin next week.\n\nThanks,\n{sender_name}",
    "Hi there,\n\nI wanted to follow up on the cost-benefit analysis for the automation project. ROI projections are very favorable.\n\nImplementation planning can begin.\n\n{sender_first}",
    "Dear all,\n\nI'm writing to announce the winners of our quarterly recognition awards. Thank you to everyone who participated.\n\nCeremony will be held next Friday.\n\nBest regards,\n{sender_name}",
    "Good afternoon,\n\nI hope your week is going well. I wanted to discuss the customer retention strategies we've been developing.\n\nPilot program ready for launch.\n\n{sender_first}",
    "Hello team,\n\nI wanted to share the results of our workplace wellness survey. Employee health and satisfaction are improving.\n\nNew programs will be introduced soon.\n\n{sender_name}",
    "Hi,\n\nI'm following up on the vendor performance review we completed. Overall scores have improved significantly.\n\nRenewal recommendations attached.\n\nThanks,\n{sender_first}",
    "Dear {recipient_type},\n\nI hope this message finds you in good spirits. I wanted to discuss the collaborative opportunity we explored.\n\nThere's potential for significant mutual benefit.\n\nBest,\n{sender_name}",
    "Good morning,\n\nI wanted to provide an update on our digital transformation roadmap. Key milestones are being achieved.\n\nProgress dashboard available online.\n\n{sender_first}",
    "Hello,\n\nI'm writing to confirm the details of our upcoming product launch event. Media coverage is confirmed.\n\nFinal preparations are in progress.\n\nBest regards,\n{sender_name}",
    "Hi everyone,\n\nI wanted to announce that we've been selected for the prestigious industry award. This recognizes our excellence.\n\nAward ceremony is next month.\n\n{sender_first}",
    "Dear team,\n\nI'm pleased to report that our employee referral program is generating excellent candidates. Thank you for your participation.\n\nReferral bonuses will be processed soon.\n\n{sender_name}",
    "Good afternoon,\n\nI hope you're having a productive day. I wanted to discuss the market penetration strategy for our new product.\n\nInitial target markets identified.\n\n{sender_first}",
    "Hello,\n\nI'm reaching out to discuss the compliance training requirements for the new regulations. All employees must complete certification.\n\nTraining portal will be available Monday.\n\nThanks,\n{sender_name}",
    "Hi there,\n\nI wanted to follow up on the continuous improvement suggestions we received. Many are being implemented.\n\nProgress updates will be shared monthly.\n\n{sender_first}",
    "Dear all,\n\nI'm writing to inform you about the new performance management system we'll be implementing. Training will be provided.\n\nRollout begins next quarter.\n\nBest regards,\n{sender_name}",
    "Good morning,\n\nI hope your week is starting strong. I wanted to share the customer loyalty program results.\n\nParticipation rates exceed expectations.\n\n{sender_first}",
    "Hello team,\n\nI wanted to provide an update on our supply chain optimization efforts. Cost savings are being realized.\n\nEfficiency improvements continue.\n\n{sender_name}",
    "Hi,\n\nI'm following up on the technology infrastructure upgrade project. Implementation is proceeding smoothly.\n\nMinimal disruption to operations.\n\nThanks,\n{sender_first}",
    "Dear {recipient_type},\n\nI hope you're doing well. I wanted to discuss the exclusive partnership opportunity we've been considering.\n\nTerms are favorable for both parties.\n\nBest,\n{sender_name}",
    "Good afternoon,\n\nI wanted to share the brand recognition survey results. Our visibility has increased significantly.\n\nMarketing efforts are paying off.\n\n{sender_first}",
    "Hello,\n\nI'm writing to confirm the logistics for our international expansion announcement. Press conference is scheduled.\n\nInvestor relations will coordinate.\n\nBest regards,\n{sender_name}",
    "Hi everyone,\n\nI wanted to announce that we've exceeded our annual sustainability goals. This demonstrates our commitment.\n\nEnvironmental impact report attached.\n\n{sender_first}",
    "Dear team,\n\nI'm pleased to share that our innovation pipeline is stronger than ever. Multiple projects show promise.\n\nInvestment decisions pending.\n\n{sender_name}",
    "Good morning,\n\nI hope you had a restful weekend. I wanted to discuss the customer feedback integration process.\n\nProduct development is incorporating insights.\n\n{sender_first}",
    "Hello,\n\nI'm reaching out regarding the leadership development program we discussed. Applications are now open.\n\nSelection process begins next month.\n\nThanks,\n{sender_name}",
    "Hi there,\n\nI wanted to follow up on the market expansion feasibility study. Results support moving forward.\n\nBusiness case development underway.\n\n{sender_first}",
    "Dear all,\n\nI'm writing to announce the implementation of our new corporate social responsibility program.\n\nEmployee volunteer opportunities available.\n\nBest regards,\n{sender_name}",
    "Good afternoon,\n\nI hope your day is productive. I wanted to discuss the operational excellence metrics we've been tracking.\n\nContinuous improvement is evident.\n\n{sender_first}",
    "Hello team,\n\nI wanted to share the results of our recent employee skills assessment. Training needs have been identified.\n\nDevelopment plans will be customized.\n\n{sender_name}",
    "Hi,\n\nI'm following up on the process automation initiative. Efficiency gains are exceeding projections.\n\nAdditional opportunities identified.\n\nThanks,\n{sender_first}",
    "Dear {recipient_type},\n\nI hope this email finds you well. I wanted to discuss the technology licensing opportunity.\n\nMutual benefits are substantial.\n\nBest,\n{sender_name}",
    "Good morning,\n\nI wanted to provide an update on our customer experience improvement program. Satisfaction scores are rising.\n\nService quality initiatives continue.\n\n{sender_first}",
    "Hello,\n\nI'm writing to confirm the details of our upcoming investor presentation. Financial results are strong.\n\nManagement team is prepared.\n\nBest regards,\n{sender_name}",
    "Hi everyone,\n\nI wanted to announce that we've achieved our diversity hiring targets ahead of schedule.\n\nInclusive workplace initiatives continue.\n\n{sender_first}"
]

current_user_emails = list(_user_email_to_uuid_map.keys())

for i in range(47):
    first = random.choice(first_names)
    last = random.choice(last_names)
    email = generate_email(first, last)
    while email in _user_email_to_uuid_map:
        email = generate_email(first, last)
    num_recipients = random.randint(0, 5)
    possible_recipients_emails = list(_user_email_to_uuid_map.keys())
    recipients_for_new_user = random.sample(possible_recipients_emails, min(num_recipients, len(possible_recipients_emails)))
    new_gmail_data = {
        "profile": {
            "emailAddress": email,
            "messagesTotal": random.randint(50, 5000),
            "threadsTotal": random.randint(20, 1500),
            "historyId": str(random.randint(1000000000000, 9999999999999))
        },
        "drafts": {},
        "labels": {},
        "messages": {},
        "threads": {}
    }
    num_drafts = random.randint(0, 2)
    for _ in range(num_drafts):
        draft_id = str(uuid.uuid4())
        new_gmail_data["drafts"][draft_id] = {
            "id": draft_id,
            "message": {
                "to": generate_email(random.choice(first_names), random.choice(last_names)),
                "from": email,
                "subject": random.choice(email_subjects),
                "body": random.choice(email_bodies).format(
                    sender_name=f"{first} {last}",
                    sender_first=first,
                    recipient_type=random.choice(["colleague", "client", "team", "partner"])
                )
            }
        }
    num_labels = random.randint(0, 4)
    for _ in range(num_labels):
        label_id = str(uuid.uuid4())
        label_name = random.choice(["Work", "Personal", "Family", "Receipts", "Travel", "Urgent", "Archive"])
        new_gmail_data["labels"][label_id] = {
            "id": label_id,
            "name": label_name,
            "messageListVisibility": random.choice(["show", "hide"]),
            "labelListVisibility": random.choice(["labelShow", "labelHide"]),
            "type": "user"
        }
    
    email_snippets = [
        "Hi, I wanted to follow up on our conversation from yesterday...",
        "Thank you for your email. I'll review the documents and get back to you...",
        "Just a quick reminder about the meeting scheduled for tomorrow...",
        "I hope this email finds you well. I wanted to discuss the proposal...",
        "Please find the attached report for your review. Let me know if you have questions...",
        "I'm writing to confirm the details we discussed earlier...",
        "Thanks for reaching out. I'd be happy to help with your inquiry...",
        "Following up on our phone call, here are the action items we discussed...",
        "I wanted to share an update on the project status...",
        "Could we schedule a call to discuss the next steps for this initiative?",
        "I've reviewed your proposal and have a few questions...",
        "Thanks for your patience while we worked through this issue...",
        "I'm reaching out to see if you're available for a quick meeting...",
        "Here's the information you requested about our services...",
        "I wanted to introduce you to our new team member who will be...",
        "Please let me know if the proposed timeline works for your schedule...",
        "I'm writing to request an extension on the current deadline...",
        "Thank you for taking the time to meet with me yesterday...",
        "I wanted to clarify a few points from our earlier discussion...",
        "Looking forward to hearing your thoughts on the draft proposal...",
        "Good morning! I hope your week is off to a great start...",
        "I'm pleased to announce that we've exceeded our quarterly targets...",
        "The budget approval process is moving forward as planned...",
        "Our customer satisfaction scores have improved significantly this quarter...",
        "I'm excited to share some positive feedback from our recent client presentation...",
        "The new product launch timeline is ahead of schedule...",
        "We've successfully completed the first phase of the digital transformation...",
        "I wanted to provide an update on our market expansion efforts...",
        "The training session feedback has been overwhelmingly positive...",
        "Our partnership negotiations are progressing well...",
        "I'm writing to confirm the logistics for our upcoming conference...",
        "The competitive analysis reveals some interesting market trends...",
        "We've received approval for the new research and development facility...",
        "The employee engagement survey results are very encouraging...",
        "I'm pleased to report that our sustainability goals are on track...",
        "The merger integration process is proceeding smoothly...",
        "Our innovation pipeline is stronger than ever before...",
        "The customer retention program is showing excellent results...",
        "We've been recognized as an industry leader in innovation...",
        "The operational efficiency improvements are delivering expected results...",
        "I wanted to discuss the preliminary budget allocations for next year...",
        "The vendor evaluation process has been completed successfully...",
        "Our diversity and inclusion metrics have improved significantly...",
        "The cybersecurity assessment results are very positive...",
        "I'm excited to share the news about our latest patent approval...",
        "The performance review process will begin next week...",
        "We've identified several opportunities for cost optimization...",
        "The customer onboarding process has been streamlined...",
        "I wanted to provide an update on our compliance audit preparation...",
        "The market research findings support our expansion strategy...",
        "Our employee referral program is generating excellent candidates...",
        "The technology infrastructure upgrade is proceeding on schedule...",
        "I'm pleased to announce the winners of our innovation challenge...",
        "The quarterly business review presentations are ready...",
        "We've achieved record sales numbers for this quarter...",
        "The strategic planning session agenda has been finalized...",
        "Our environmental sustainability efforts are showing measurable results...",
        "The leadership development program applications are now open...",
        "I wanted to share the customer testimonials we've received...",
        "The supply chain optimization project is delivering cost savings...",
        "We've successfully implemented the new quality control measures...",
        "The annual conference registration numbers exceed expectations...",
        "I'm writing to confirm the details of our upcoming audit...",
        "The professional development opportunities catalog is now available...",
        "Our brand recognition has increased significantly in target markets...",
        "The process automation initiative is yielding impressive results...",
        "I wanted to discuss the feedback from our recent board presentation...",
        "The customer experience improvement program is showing positive trends...",
        "We've been selected as a finalist for the industry innovation award...",
        "The workplace wellness survey results indicate high satisfaction...",
        "I'm pleased to report that our patent portfolio has grown...",
        "The succession planning framework has been developed...",
        "Our competitive intelligence analysis reveals new opportunities...",
        "The international expansion timeline has been approved...",
        "I wanted to provide an update on our artificial intelligence initiative...",
        "The employee skills assessment has identified training needs...",
        "We've achieved our diversity hiring targets ahead of schedule...",
        "The customer loyalty program participation rates are excellent...",
        "I'm writing to announce the new corporate social responsibility program...",
        "The operational excellence metrics show continuous improvement...",
        "Our technology licensing opportunity presents mutual benefits...",
        "The performance improvement plan implementation begins next quarter...",
        "I wanted to share the results of our employee satisfaction survey...",
        "The risk assessment mitigation strategies are being implemented...",
        "We've received industry certification for our quality management system...",
        "The mentorship program has generated overwhelming interest...",
        "I'm pleased to announce the expansion of our global operations...",
        "The cost-benefit analysis for automation shows favorable ROI...",
        "Our supplier diversity initiative is showing encouraging results...",
        "The joint research project proposal has been submitted...",
        "I wanted to discuss the proposed organizational structure changes...",
        "The continuous improvement suggestions are being implemented...",
        "We've exceeded our annual sustainability goals...",
        "The new performance management system rollout begins soon...",
        "I'm writing to confirm the international partnership agreement...",
        "The customer focus group insights are valuable for development...",
        "Our market penetration strategy for the new product is ready...",
        "The compliance training requirements for new regulations are mandatory...",
        "I wanted to provide an update on our community outreach program...",
        "The digital marketing campaign metrics exceed expectations...",
        "We've achieved significant improvements in operational efficiency...",
        "The product demonstration logistics have been confirmed...",
        "I'm pleased to share that our innovation metrics are strong...",
        "The leadership succession planning process is underway...",
        "Our customer acquisition costs have decreased substantially...",
        "The market expansion feasibility study supports moving forward...",
        "I wanted to discuss the exclusive partnership opportunity...",
        "The brand awareness survey results show positive trends...",
        "We've implemented new data privacy protocols...",
        "The quarterly recognition awards ceremony is scheduled...",
        "I'm writing to announce the new employee benefits package...",
        "The vendor performance review scores have improved...",
        "Our workplace diversity metrics continue to improve...",
        "The strategic alliance negotiations are progressing well...",
        "I wanted to share the preliminary market research findings...",
        "The customer service quality improvements are measurable...",
        "We've been approved for the prestigious industry certification...",
        "The talent acquisition strategy is yielding excellent results...",
        "I'm pleased to report that our innovation pipeline is robust...",
        "The enterprise resource planning system upgrade is complete...",
        "Our customer retention strategies are proving effective...",
        "The business continuity planning process has been updated...",
        "I wanted to discuss the intellectual property portfolio review...",
        "The employee development program evaluation shows positive outcomes...",
        "We've successfully launched our new customer portal...",
        "The market positioning analysis supports our current strategy...",
        "I'm writing to confirm the product launch event details...",
        "The supply chain resilience improvements are being implemented...",
        "Our environmental impact reduction goals are being met...",
        "The technology roadmap for digital transformation is approved...",
        "I wanted to provide an update on our innovation lab progress...",
        "The customer feedback integration process is working effectively...",
        "We've achieved breakthrough results in our research project...",
        "The organizational culture assessment results are encouraging...",
        "I'm pleased to announce our selection for the innovation award...",
        "The process reengineering initiative is delivering expected benefits...",
        "Our market share in key segments continues to grow...",
        "The stakeholder engagement strategy is yielding positive results...",
        "I wanted to discuss the preliminary findings from our analysis...",
        "The customer journey mapping exercise has revealed insights...",
        "We've implemented enhanced security protocols across all systems...",
        "The performance dashboard provides real-time visibility...",
        "I'm writing to announce the successful completion of our merger...",
        "The competitive benchmarking study results are available...",
        "Our employee engagement scores have reached record levels...",
        "The innovation ecosystem we've built is generating ideas...",
        "I wanted to share the customer advocacy program results...",
        "The business model transformation is ahead of schedule...",
        "We've established new partnerships in emerging markets...",
        "The quality assurance metrics show consistent improvement...",
        "I'm pleased to report that our expansion plans are approved...",
        "The digital customer experience enhancements are live...",
        "Our research and development investments are paying dividends...",
        "The change management program is facilitating smooth transitions...",
        "I wanted to discuss the long-term strategic vision...",
        "The customer success metrics demonstrate strong value delivery...",
        "We've achieved certification in multiple international standards...",
        "The innovation culture we've fostered is producing results...",
        "I'm writing to confirm the partnership agreement terms...",
        "The market opportunity assessment reveals significant potential...",
        "Our agile transformation journey is showing measurable progress...",
        "The customer-centric approach is improving satisfaction scores...",
        "I wanted to provide an update on our sustainability initiatives...",
        "The digital innovation platform is enabling rapid development...",
        "We've successfully integrated the acquired company operations...",
        "The performance management framework is driving accountability...",
        "I'm pleased to announce our industry leadership recognition...",
        "The data analytics capabilities are providing actionable insights...",
        "Our talent development programs are building future leaders...",
        "The customer experience optimization efforts are yielding results...",
        "I wanted to discuss the strategic partnership expansion...",
        "The operational excellence journey continues to deliver value...",
        "We've launched our comprehensive sustainability program...",
        "The innovation methodology we've adopted is proving effective...",
        "I'm writing to share the annual performance review results...",
        "The market entry strategy for new regions is finalized...",
        "Our commitment to diversity and inclusion is showing impact...",
        "The technology modernization program is transforming operations...",
        "I wanted to provide an update on our customer value proposition...",
        "The collaborative culture we've built is fostering innovation...",
        "We've achieved significant milestones in our growth strategy...",
        "The customer insights platform is driving product development...",
        "I'm pleased to report that our vision is becoming reality...",
        "The ecosystem of partners we've built is creating synergies...",
        "Our focus on operational excellence is delivering results...",
        "The strategic initiatives we've launched are gaining momentum...",
        "I wanted to discuss the future roadmap for our industry...",
        "The customer-first philosophy is embedded in our culture...",
        "We've established ourselves as thought leaders in innovation...",
        "The transformation journey we've embarked on is succeeding...",
        "I'm writing to confirm our commitment to sustainable growth...",
        "The value creation model we've developed is working...",
        "Our investment in people and technology is paying off...",
        "The market leadership position we've achieved is sustainable...",
        "I wanted to share our vision for the next phase of growth..."
    ]

    num_messages = random.randint(5, 50)
    user_message_ids = []

    first2 = random.choice(first_names2)
    last2 = random.choice(last_names2)
    all_possible_recipients = list(_user_email_to_uuid_map.keys()) + [generate_email(first2, last2)]
    
    for msg_idx in range(num_messages):
        msg_id_old_placeholder = f"temp_msg_{i}_{msg_idx}"
        sender = random.choice([email, random.choice(recipients_for_new_user) if recipients_for_new_user else generate_email("random", "sender")])
        recipient = random.choice([email, random.choice(all_possible_recipients)])
        headers = [
            {"name": "From", "value": sender},
            {"name": "To", "value": recipient},
            {"name": "Subject", "value": random.choice(email_subjects)}
        ]
        is_unread = random.random() < 0.3
        label_ids = ["INBOX"]
        if is_unread:
            label_ids.append("UNREAD")
        if random.random() < 0.1:
            label_ids.append("STARRED")
        if random.random() < 0.05:
            label_ids.append("SPAM")
        new_gmail_data["messages"][msg_id_old_placeholder] = {
            "id": msg_id_old_placeholder,
            "threadId": f"temp_thread_{i}_{msg_idx}",
            "snippet": random.choice(email_snippets),
            "payload": {"headers": headers},
            "internalDate": generate_random_past_timestamp(365),
            "labelIds": label_ids,
            "original_id": msg_id_old_placeholder,
        }
        user_message_ids.append(msg_id_old_placeholder)
    num_threads_to_create = random.randint(min(5, num_messages // 2), min(15, num_messages // 2))
    threads_dict_for_user = {}
    if user_message_ids:
        for _ in range(num_threads_to_create // 2):
            if len(user_message_ids) >= 2:
                thread_msg_ids = random.sample(user_message_ids, random.randint(2, min(5, len(user_message_ids))) )
                thread_uuid = str(uuid.uuid4())
                for mid in thread_msg_ids:
                    new_gmail_data["messages"][mid]["threadId"] = thread_uuid
                user_message_ids = [m for m in user_message_ids if m not in thread_msg_ids]
        for msg_id in user_message_ids:
            new_gmail_data["messages"][msg_id]["threadId"] = str(uuid.uuid4())
    user_id, user_data = _create_user_data(email, first, last, recipients_for_new_user, new_gmail_data)
    DEFAULT_STATE["users"][user_id] = user_data
    current_user_emails.append(email)

all_user_uuids = list(_user_email_to_uuid_map.values())

for user_id, user_data in DEFAULT_STATE["users"].items():
    resolved_recipients = []
    for recipient_item in user_data["recipients"]:
        if recipient_item in _user_email_to_uuid_map:
            resolved_recipients.append(_user_email_to_uuid_map[recipient_item])
        elif recipient_item in all_user_uuids:
            resolved_recipients.append(recipient_item)
    user_data["recipients"] = list(set([f for f in resolved_recipients if f != user_id]))

print(f"Total number of users generated: {len(DEFAULT_STATE['users'])}")

output_filename = 'diverse_gmail_state.json'

with open(output_filename, 'w') as f:
    json.dump(DEFAULT_STATE, f, indent=2)

print(f"Generated DEFAULT_STATE saved to '{output_filename}'")

if DEFAULT_STATE["users"]:
    sample_user_id = list(DEFAULT_STATE["users"].keys())[random.randint(0, len(DEFAULT_STATE["users"]) - 1)]
    print(f"\nSample data for user {DEFAULT_STATE['users'][sample_user_id]['first_name']} {DEFAULT_STATE['users'][sample_user_id]['last_name']}:")
    print(json.dumps(DEFAULT_STATE["users"][sample_user_id], indent=2))