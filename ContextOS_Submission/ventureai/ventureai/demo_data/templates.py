# Realistic enterprise templates for recruiter logs, meetings, emails, placements, and feedback.

SCENARIO_TEMPLATES = {
    "Urgent Hiring": {
        "recruiter_notes": [
            "Candidate is highly motivated by the urgent timeline and can start immediately.",
            "Candidate is willing to skip final rounds of other companies to expedite this process.",
            "Candidate has strong hands-on experience that aligns 100% with the client's critical stack needs.",
            "Candidate is available for back-to-back technical rounds this week."
        ],
        "meeting_notes": [
            "Hiring manager emphasized that filling this role is the department's top priority this quarter.",
            "Meeting focused on bypassing minor feedback items to secure the candidate as soon as possible.",
            "Client requested all qualified resumes to be submitted within 48 hours.",
            "Interview panel has cleared calendars to accommodate same-day debriefs."
        ],
        "crm_updates": [
            "Marked position as urgent. Recruiter resource allocation increased.",
            "Sent client a curated batch of 3 senior profiles. Immediate feedback requested.",
            "Client confirmed they will fast-track candidate to final manager round.",
            "Urgent follow-up call scheduled with HR Director."
        ],
        "emails": [
            {
                "subject": "URGENT: Candidate Submission - [Candidate Name] - [Job Title]",
                "body": "Dear [Client Contact],\n\nI hope this email finds you well.\n\nFollowing our discussion regarding the urgent opening for the [Job Title] role, I am pleased to submit [Candidate Name]. They have over [Experience Years] years of experience, specializing in the exact tech stack required for this project.\n\n[Candidate Name] is available to start immediately and can interview tomorrow. Let me know if you would like me to set up a technical round.\n\nBest regards,\n[Recruiter Name]\nXLVentures Staffing"
            }
        ]
    },
    "Client At Risk": {
        "recruiter_notes": [
            "Candidate noticed client's recent negative reviews but remains interested if salary is right.",
            "Candidate expressed slight concern regarding potential project reorganization at client.",
            "Recruiter advised candidate to emphasize stability and long-term commitment in client conversations."
        ],
        "meeting_notes": [
            "Client expressed frustration over slow sourcing speed for this critical role.",
            "Discussed account health; client mentioned looking at alternative agencies if we don't submit soon.",
            "Hiring manager rejected recent submittals, claiming mismatch in communication skills.",
            "Aligned on updated candidate criteria to rebuild trust with the accounts team."
        ],
        "crm_updates": [
            "Account status flagged for review. Partner intervention requested.",
            "Scheduled weekly sync with client's VP of Engineering to restore confidence.",
            "Completed calibration call with client HR team.",
            "Client extended SLA by two weeks to evaluate our pipeline."
        ],
        "emails": [
            {
                "subject": "XLVentures Partnership Sync & Pipeline Update: [Job Title]",
                "body": "Dear [Client Contact],\n\nThank you for sharing your feedback during our call yesterday. We take your concerns seriously and have dedicated two additional senior recruiters to the [Job Title] search.\n\nWe have identified a strong candidate, [Candidate Name], who brings extensive experience matching your criteria. I have attached their resume for your review and look forward to your thoughts.\n\nBest regards,\n[Recruiter Name]\nXLVentures Staffing"
            }
        ]
    },
    "Candidate Ghosting": {
        "recruiter_notes": [
            "Candidate failed to show up for scheduled prep call; left voicemail.",
            "Candidate unresponsive to multiple follow-ups via email and LinkedIn message.",
            "Marked candidate profile as low responsiveness; potential flight risk."
        ],
        "meeting_notes": [
            "Client inquired about candidate status as they did not join the scheduled interview bridge.",
            "Apologized to hiring manager for candidate's absence. Committed to providing replacement candidates.",
            "Discussed alternative profiles to keep the timeline on track."
        ],
        "crm_updates": [
            "Candidate status set to inactive. Reason: Failed to attend scheduled client interview.",
            "Sent candidate official withdrawal of submittal notification.",
            "Archived candidate application for this job ID."
        ],
        "emails": [
            {
                "subject": "Interview Status Update: [Candidate Name] - [Job Title]",
                "body": "Dear [Client Contact],\n\nI am writing to apologize for the inconvenience caused today. [Candidate Name] did not join our scheduled interview call. I have reached out to them but have not received a response.\n\nWe hold our candidates to high professional standards and are immediately withdrawing them from consideration. I am already preparing two replacement submissions for your review.\n\nBest regards,\n[Recruiter Name]\nXLVentures Staffing"
            }
        ]
    },
    "Counter Offer": {
        "recruiter_notes": [
            "Candidate received a counter-offer from their current employer with a 15% salary increase.",
            "Discussed candidate motivation; they prefer our client's role but need competitive matching.",
            "Candidate requested time to weigh career growth options against the counter-offer."
        ],
        "meeting_notes": [
            "Presented candidate counter-offer scenario to client HR team.",
            "Client willing to increase base compensation to keep candidate in play.",
            "Hiring manager stressed that candidate's skills are essential and urged HR to match."
        ],
        "crm_updates": [
            "Candidate status updated: Counter-Offer pending decision.",
            "Submitted updated salary requirements to client compensation committee.",
            "Client approved salary revision. Awaiting candidate decision."
        ],
        "emails": [
            {
                "subject": "Offer Discussion: Update on [Candidate Name] - [Job Title]",
                "body": "Dear [Client Contact],\n\nI want to share a quick update regarding [Candidate Name]. They have received a strong counter-offer from their current company.\n\n[Candidate Name] remains very excited about the [Job Title] opportunity with your team. If we can adjust the base offer slightly, I am confident they will sign immediately. Let me know if we can schedule a quick call to discuss.\n\nBest regards,\n[Recruiter Name]\nXLVentures"
            }
        ]
    },
    "Salary Negotiation": {
        "recruiter_notes": [
            "Candidate's salary expectations increased due to competing verbal offer.",
            "Candidate willing to accept if sign-on bonus is offered in lieu of higher base.",
            "Advised candidate that client's budget limits base salary flexibility."
        ],
        "meeting_notes": [
            "Discussed candidate's salary expectations. Client confirmed base is capped but can offer performance bonuses.",
            "Client HR department reviewing equity allocation to bridge the salary gap.",
            "Hiring manager agreed to make a case for a budget exception to the business unit head."
        ],
        "crm_updates": [
            "Offer details updated in CRM. Base salary adjustments under review.",
            "Client requested candidate's current W2 or compensation details for validation.",
            "Negotiations ongoing. Candidate response expected by Friday."
        ],
        "emails": [
            {
                "subject": "Compensation Calibration: [Candidate Name] - [Job Title]",
                "body": "Dear [Client Contact],\n\nI am writing to follow up on our offer discussion for [Candidate Name].\n\nThey are highly interested in joining, but are currently evaluating another opportunity that offers a slightly higher base. They have asked if there is any flexibility to bring the base salary to the target range or adjust the equity component.\n\nI believe a small adjustment will secure this hire. Let's connect soon.\n\nBest regards,\n[Recruiter Name]\nXLVentures"
            }
        ]
    },
    "Multiple Offers": {
        "recruiter_notes": [
            "Candidate has two active offers from major tech firms and is deciding this week.",
            "Candidate likes the team culture at our client but is attracted to the equity elsewhere.",
            "Stressed the career development path and mentorship opportunities at our client."
        ],
        "meeting_notes": [
            "Informed hiring manager of candidate's multiple offers. Urged fast decision-making.",
            "Client agreed to schedule a peer-to-peer call with candidate to win them over.",
            "Discussed team growth plans to present a compelling vision to the candidate."
        ],
        "crm_updates": [
            "Candidate flagged as high priority due to competing active offers.",
            "Organized post-interview cultural fit sync between candidate and engineering team lead.",
            "Sent candidate marketing materials highlighting client's market success."
        ],
        "emails": [
            {
                "subject": "Status Update: [Candidate Name] - [Job Title]",
                "body": "Dear [Client Contact],\n\nI wanted to let you know that [Candidate Name] has progressed to final offers with two other companies.\n\nThey have indicated that your team is their preferred choice. To secure them, I recommend extending the formal offer as soon as possible so we do not lose momentum. I will keep you updated.\n\nBest regards,\n[Recruiter Name]\nXLVentures"
            }
        ]
    },
    "Interview Delay": {
        "recruiter_notes": [
            "Candidate frustrated by the long delay between interview rounds; remains interested but active.",
            "Candidate scheduled another interview due to lack of feedback from our client.",
            "Advised candidate that client's hiring manager is currently traveling."
        ],
        "meeting_notes": [
            "Client apologized for internal delays due to project release cycles.",
            "Aligned on schedule for next round; confirmed next Tuesday afternoon.",
            "Hiring manager promised to deliver final decisions within 24 hours of the interview."
        ],
        "crm_updates": [
            "Rescheduled postponed second-round interview.",
            "Sent status update email to candidate to keep them warm.",
            "Client contact notified of risk of candidate dropping out due to delay."
        ],
        "emails": [
            {
                "subject": "Next Steps & Interview Scheduling: [Candidate Name] - [Job Title]",
                "body": "Dear [Client Contact],\n\nI hope you are doing well.\n\n[Candidate Name] has completed the initial assessment and is looking forward to the next round. I wanted to check your availability for next week so we can schedule the technical interview and keep the momentum going.\n\nPlease let me know a few slots that work for you.\n\nBest regards,\n[Recruiter Name]\nXLVentures"
            }
        ]
    },
    "Hiring Freeze": {
        "recruiter_notes": [
            "Candidate disappointed by position pause but willing to be kept in talent pool.",
            "Recruiter noted candidate skills are general enough to map to other open roles.",
            "Scheduled future follow-up call with candidate in 4 weeks."
        ],
        "meeting_notes": [
            "Client informed us of a corporate hiring freeze affecting all non-essential positions.",
            "Discussed impact on candidate pipeline. Agreed to pause active recruiting on this JD.",
            "Client hopes to reopen the role next quarter and requested us to keep candidates warm."
        ],
        "crm_updates": [
            "Job status updated to Paused/Hiring Freeze.",
            "Notified all in-process candidates of role status change.",
            "Set task to re-evaluate account status in 30 days."
        ],
        "emails": [
            {
                "subject": "Recruiting Update: [Job Title] Requisition Status",
                "body": "Dear [Client Contact],\n\nThank you for the update regarding the current hiring freeze. We understand the adjustments being made at the corporate level.\n\nWe have paused our active search on the [Job Title] role. I will keep in touch with the current candidates to maintain interest, so we are ready to restart quickly when the freeze is lifted.\n\nBest regards,\n[Recruiter Name]\nXLVentures"
            }
        ]
    },
    "Position Closed": {
        "recruiter_notes": [
            "Candidate informed that the role was closed; offered to submit them for similar roles.",
            "Candidate appreciated the timely update and communication."
        ],
        "meeting_notes": [
            "Client confirmed they hired an internal candidate for the position.",
            "Conducted debrief; client expressed appreciation for the quality of submissions.",
            "Discussed potential future openings in the DevOps department."
        ],
        "crm_updates": [
            "Job status set to Closed/Filled Internally.",
            "Sent pipeline closure notifications to candidate pool.",
            "Updated placements status registry."
        ],
        "emails": [
            {
                "subject": "Search Completion: [Job Title] Requisition",
                "body": "Dear [Client Contact],\n\nThank you for letting us know that the [Job Title] position has been filled. We are glad to hear that you found a suitable candidate internally.\n\nWe will archive the pipeline for this search. It has been a pleasure working with you, and we look forward to partnering on future hiring needs.\n\nBest regards,\n[Recruiter Name]\nXLVentures"
            }
        ]
    },
    "Offer Accepted": {
        "recruiter_notes": [
            "Candidate formally accepted the client's offer and signed the contract.",
            "Candidate confirmed resignation submitted to current employer; start date set.",
            "Recruiter sent onboarding guide and welcome message."
        ],
        "meeting_notes": [
            "Client expressed excitement that candidate accepted the offer.",
            "Discussed first-day logistics, background checks, and equipment delivery.",
            "Confirmed billing and placement terms contract details."
        ],
        "crm_updates": [
            "Placement recorded. Success status flag activated.",
            "Candidate profile updated to Placed.",
            "Invoiced client finance department for placement fee."
        ],
        "emails": [
            {
                "subject": "Offer Accepted! Onboarding Details - [Candidate Name] - [Job Title]",
                "body": "Dear [Client Contact],\n\nI am thrilled to share that [Candidate Name] has officially signed the offer letter for the [Job Title] position!\n\nThey have submitted their resignation and are confirmed to start on [Placement Date]. I will coordinate the onboarding process with your HR department this week.\n\nThank you for your partnership in making this placement a success.\n\nBest regards,\n[Recruiter Name]\nXLVentures"
            }
        ]
    },
    "Offer Declined": {
        "recruiter_notes": [
            "Candidate declined the offer due to better work-life balance at competing firm.",
            "Candidate expressed regret but decided to prioritize shorter commute time.",
            "Recruiter analyzed declining factor: location distance was primary driver."
        ],
        "meeting_notes": [
            "Client disappointed by candidate's decline. Discussed compensation adjustments for future candidates.",
            "Hiring manager requested we resume sourcing immediately with expanded budget.",
            "Aligned on location flexibility/hybrid options to increase candidate acceptance rate."
        ],
        "crm_updates": [
            "Placement status set to Offer Declined.",
            "Restarted active search pipeline. Sourcing fresh candidates.",
            "Updated compensation metrics for the job ID."
        ],
        "emails": [
            {
                "subject": "Offer Status Update: [Candidate Name] - [Job Title]",
                "body": "Dear [Client Contact],\n\nI am writing to share that [Candidate Name] has decided to decline the offer for the [Job Title] role. They have accepted another position that is closer to their residence.\n\nWhile this is disappointing, we have already re-engaged our pipeline and have identified two strong backup candidates. I will send their profiles shortly.\n\nBest regards,\n[Recruiter Name]\nXLVentures"
            }
        ]
    }
}

INTERVIEW_FEEDBACK_TEMPLATES = [
    {"feedback": "Technical Strong. Demonstrated deep knowledge of Python and distributed systems architecture.", "rating": 5},
    {"feedback": "Communication Excellent. Explained complex database optimization techniques with great clarity.", "rating": 5},
    {"feedback": "System Design Weak. Struggled to design a highly scalable message queue system.", "rating": 3},
    {"feedback": "Culture Fit Good. Aligns well with the engineering values and team collaboration standards.", "rating": 4},
    {"feedback": "Salary Misaligned. Candidate expectations exceed client's max salary range for this grade.", "rating": 2},
    {"feedback": "Skills gap. Candidate lacked hands-on experience with Kubernetes and CI/CD tools.", "rating": 3},
    {"feedback": "Coding Excellent. Solved all algorithmic challenges efficiently with clean, readable code.", "rating": 5}
]

RECRUITER_NAMES = [
    "Sarah Jenkins",
    "Michael Chang",
    "David Miller",
    "Emily Rodriguez",
    "James Wilson",
    "Jessica Taylor"
]
