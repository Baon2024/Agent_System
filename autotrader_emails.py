from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Autotrader Emails', 0, 1, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 10, body)
        self.ln()

pdf = PDF()
pdf.add_page()

# Email 1
pdf.chapter_title('Subject: We’ve updated our Privacy Notice')
pdf.chapter_body('From: Autotrader <comms@service.autotrader.co.uk>\nDate: Wed, 06 May 2026 10:02:56 +0000\n\nContent:\nWe’ve updated our Privacy Notice\nHi there,\nWe’re getting in touch to let you know that our Privacy Notice has recently been updated.\nThe main changes are:\n- We’ve added details about our complaints process and a new contact email for complaints, as required by the recently introduced Data Use and Access Act 2025 (DUAA).\n- We’ve referenced that we rely on the new Recognised Legitimate Interest (introduced by DUAA) for certain types of processing, including fraud and disclosure of personal data to public authorities such as the police.\n- The wording has been refreshed in places to make things clearer and easier to understand.\nOtherwise, everything remains as it was.')

# Email 2
pdf.chapter_title('Subject: Welcome to Auto Trader')
pdf.chapter_body('From: Auto Trader <comms@service.autotrader.co.uk>\nDate: Sun, 12 Nov 2023 05:20:16 +0000\n\nContent:\nEverything you need to buy or sell your next vehicle, in one place.\nWELCOME TO Auto Trader\nWhether you\'re looking to buy a new car, or sell your current one, we\'re here to help.\nMake the most of your account:\n- Save & compare: Save and compare your favourite cars all in one place.\n- Free car valuation: The car on your driveway could be worth more than you think!\n- Expert reviews & video: The latest car reviews, news and advice from our expert team.\n- Do more from home: Skip the showrooms and get a car delivered straight to your doorstep.')

pdf.output('autotrader_emails.pdf')