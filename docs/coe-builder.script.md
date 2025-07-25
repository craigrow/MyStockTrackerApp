# COE Builder Script

## Overview

This script automates the creation of a Correction of Error (COE) document from a Ticket or SIM issue. A COE is a document that helps identify root causes of incidents and share learnings to prevent similar issues in the future. The script extracts relevant information from the input source, structures it according to Amazon's COE template, and creates both a local HTML file and a shareable Quip document.

## Parameters

- **issue_id** (required): The ID of the ticket (e.g., P123456789) or SIM issue to convert to a COE
- **is_amazon_stores** (required): If the issue effected Amazon Stores
- **output_path** (optional, default: current directory): Directory where the HTML file will be saved
- **create_quip** (optional, default: true): Whether to create a Quip document in addition to the local file

**Constraints for parameter acquisition:**
- The model MUST ask for the issue_id if not provided
- The model MUST support both ticket IDs (starting with P, T, or V) and SIM issue IDs
- The model SHOULD verify the issue_id format before proceeding




## Steps

### 1. Gather Information from the Ticket or SIM

**Constraints:**
- The model MUST determine if the input is a ticket or SIM issue based on the ID format
- If the input is a ticket, the model MUST use the amzn_mcp___read_internal_website tool to read the content from t.corp.amazon.com
- If the input is a SIM issue, the model MUST use the amzn_mcp___sim_get_issue tool to read its content
- The model MUST extract all relevant information including comments, attachments, and timeline events
- The model MUST examine all available tabs for tickets (Overview, Communication, Information, Event Management, Audit Trail)
- The model SHOULD extract all charts and graphs from the issue comments

### 2. Extract and Process Charts and Graphs

**Constraints:**
- The model MUST identify and extract all charts and graphs from the issue
- For each chart or graph, the model MUST:
  - Extract the image URL
  - Identify what the chart represents (order rates, errors, traffic, etc.)
  - Create properly formatted HTML image with descriptive alt text
  - Add a caption explaining what the chart shows and its significance
  - Include the source link if available
- The model MUST organize charts in a logical sequence that tells the story of the incident
- The model SHOULD look for common chart types including:
  - Order rate comparisons (Day-over-Day, Week-over-Week)
  - Error rates and correlations with order drops
  - Traffic patterns and anomalies
  - Service health metrics
  - Screenshots showing specific error conditions

### 3. Fetch Current Template Structure

**Constraints:**
- The model MUST first fetch the current COE template from https://code.amazon.com/packages/AwsCoeLambdaOps/blobs/mainline/--/src/main/resources/amazonDefaultText.md?raw=1
- The model MUST parse the template to extract the exact section headings in their correct order
- if is_amazon_stores then replace "When was the last Operational Readiness Review (ORR) performed?" with "When was the last Technical Risk Assessment (TRA or LTRA) performed?"
- if is_amazon_stores then replace "is there an existing ORR recommendation" with "is there an existing TRA recommendation"
- The model MUST store these headings for reference during content generation
- The model MUST NOT rely on hardcoded section names that could become outdated

### 4. Generate the COE Content

**Constraints:**

1. The model MUST use the structure defined in the current template, creating the exact same sections and headings in the same order as extracted in Step 3
1. The model MUST follow specific guidelines for each section as defined in the current template
1. The model MUST use the exact section names as extracted from the template, with no deviations or substitutions
1. The model MUST NOT use alternative names for sections (e.g., "Executive Summary" instead of "Summary") even if they seem equivalent
1. If is_amazon_stores the model MUST follow the specific guidelines in https://w.amazon.com/bin/view/Consumer/OpsMetrics/COE_Review/
1. The model MUST use proper HTML formatting with appropriate heading hierarchy
1. The model MUST include placeholder text for sections where information is not available 
1. The model MUST include all charts and graphs from the SIM issue comments.
   1. For each chart or graph:
      1. Include the image using the HTML image syntax 
       111. Add a brief caption describing what the chart shows 
       111. Include the source link if available
1. The model MUST ensure all references between sections (RC, LL, AI) are consistent
1. The model SHOULD follow guidelines in https://w.amazon.com/bin/view/COE/UserGuide/BestPractices/
1. The model SHOULD follow guidelines in https://w.amazon.com/bin/view/JahoodBlog/2024/03-08-common-coe-pitfalls/
1. If is_aws_stores the model MUST follow the guidelines in https://w.amazon.com/bin/view/Users/wexlerm/COE-tips/ only if is_amazon_stores
2. The timeline section MUST begin with defect injection and MUST end with defect removal.

### 5. Save the COE Content to a File

**Constraints:**
- The model MUST save the fully prepared COE content to a file named "COE_{issue_id}.html"
- The model MUST use the fs_write tool with the create command
- The model MUST ensure the file is properly formatted with all necessary HTML tags
- The model MUST save the file to the specified output_path or current directory if not specified

### 6. Create a Quip Document (if requested)

**Constraints:**
- If create_quip is true, the model MUST create a Quip document using the amzn_mcp___create_quip tool
- The model MUST use the following parameters:
  - title: "COE {issue_id} - {concise_title}"
  - format: "html"
  - content: The fully prepared COE content from the saved file
- The model MUST confirm successful creation of the Quip document
- The model MUST provide the URL of the newly created document

### 7. Provide Summary and Next Steps

**Constraints:**
- The model MUST provide a summary of the COE creation process
- The model MUST list the key sections of the COE and their contents
- The model MUST highlight any areas that need further input from the team
- The model MUST suggest next steps for stakeholders (review, comment, update)
- The model SHOULD provide the file path of the local HTML file and the URL of the Quip document

## Examples

https://www.coe.a2z.com/coe/93906/content

### Example Input
```
Create a COE from ticket P123456789
```

## Troubleshooting

### Access Issues
If the model encounters access issues when trying to read the ticket or SIM issue, it should verify that the issue ID is correct and that the user has appropriate permissions.

### Missing Information
If critical information is missing from the source, the model should create the COE with placeholder text clearly marked for the team to fill in later.

### Image Processing Issues
If images or charts cannot be properly extracted or processed, the model should note this in the COE and provide instructions for manually adding them.
