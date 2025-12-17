# Feedback & Rerun Extraction Feature

## ✅ Feature Overview

Added the ability to provide feedback and rerun the extraction to refine results without re-uploading files.

## 🎯 What You Can Do

1. **Provide Feedback**: After viewing extracted requirements, add feedback in a text box
2. **Rerun Extraction**: Click "Rerun Extraction with Feedback" to process again with your guidance
3. **Refine Results**: Iteratively improve the extraction based on your corrections

## 📍 Location in UI

The feedback section appears **after the Download Results section**, at the bottom of the extracted requirements view.

## 💡 How to Use

### Step 1: Review Results
- After extraction completes, review the extracted requirements in the tabs
- Identify any issues, missing items, or areas needing improvement

### Step 2: Provide Feedback
Enter your feedback in the text area, for example:
```
- Focus more on supplier requirements
- The PO number mentioned should be included
- Add more details about non-functional requirements
- Correct terminology: use "supplier" not "sublatures"
- Missing action items from the discussion
```

### Step 3: Rerun Extraction
- Click the **"🔄 Rerun Extraction with Feedback"** button
- The extraction will run again, incorporating your feedback
- Results will update automatically

### Step 4: Iterate (Optional)
- If needed, provide additional feedback and rerun again
- Each iteration improves the extraction based on your guidance

## ✨ Key Features

### Feedback Input Box
- Large text area for detailed feedback
- Placeholder with examples
- Help text explaining how to use it

### Rerun Button
- Processes extraction with your feedback
- Shows progress indicator
- Updates results automatically

### Clear Feedback Button
- Easily clear the feedback box
- Start fresh for new feedback

## 🎯 Use Cases

### 1. **Terminology Corrections**
```
- Use "PO number" instead of "Pyo number"
- Use "supplier" instead of "sublatures"
```

### 2. **Missing Requirements**
```
- Add requirements about data security
- Include performance requirements that were discussed
```

### 3. **Priority Adjustments**
```
- Mark the authentication feature as High priority
- Business rules section needs more detail
```

### 4. **Context Enhancements**
```
- Include more context from the discussion
- Add assumptions that were mentioned
```

### 5. **Focus Areas**
```
- Focus more on supplier-related requirements
- Emphasize action items with deadlines
```

## 🔧 Technical Details

### Implementation

1. **Feedback Parameter**: Added `feedback` parameter to extraction functions
2. **Prompt Enhancement**: Extraction prompt includes feedback section when provided
3. **UI Components**: Feedback text area and rerun button in results section

### How It Works

1. User provides feedback in text area
2. Feedback is passed to extraction function
3. Extraction prompt is enhanced with feedback context
4. AI processes transcript with feedback guidance
5. Results are updated automatically

## 📝 Example Feedback

### Good Feedback Examples:

**Specific Corrections:**
```
- Change "Pyo number" to "PO number" throughout
- Use "supplier" terminology consistently
```

**Missing Items:**
```
- Add the security requirements that were discussed around 15 minutes in
- Include the deadline for the login feature (mentioned as Q2 2024)
```

**Focus Areas:**
```
- Emphasize supplier onboarding requirements
- Extract more details about the payment integration
```

**Priority Guidance:**
```
- The authentication feature should be marked as High priority
- Data migration requirements are critical (High priority)
```

## ⚠️ Tips for Best Results

1. **Be Specific**: Clear, specific feedback works better than vague requests
2. **Use Examples**: Reference specific parts of the conversation when possible
3. **Iterate**: Start with high-level feedback, then refine with details
4. **Clear Language**: Use clear, direct language in your feedback

## 🚀 Benefits

- ✅ **No Re-upload Needed**: Refine results without re-processing files
- ✅ **Iterative Improvement**: Multiple passes to perfect extraction
- ✅ **Time Saving**: Faster refinement than re-uploading
- ✅ **Better Accuracy**: User guidance improves AI understanding
- ✅ **User Control**: You direct what to focus on

## 📊 Workflow

```
Upload File → Extract Requirements → Review Results
                                          ↓
                                    Provide Feedback
                                          ↓
                              Rerun Extraction with Feedback
                                          ↓
                                    Review Updated Results
                                          ↓
                         (Optional) Iterate with More Feedback
```

---

## 🎉 Summary

This feature allows you to:
- Provide feedback on extraction results
- Rerun extraction without re-uploading files
- Iteratively refine and improve results
- Get better, more accurate extractions with your guidance

**Location**: After the Download Results section in the requirements view

**Status**: ✅ **Fully Implemented and Ready to Use!**

---

Last Updated: 2025-12-02


