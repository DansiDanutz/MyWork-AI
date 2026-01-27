# Phase 5: File Attachments - Implementation Context

**Generated:** 2026-01-25
**Phase Goal:** Users can attach and manage files on their tasks

## Implementation Decisions

### Upload Interface

- **Method**: Drag & drop only interface (modern, intuitive UX)
- **Progress**: Progress bar with percentage for clear upload feedback
- **Multiple Files**: Upload all selected files simultaneously for speed

### File Display & Management

- **Primary Location**: Show file indicators on task cards in list view
- **Secondary Feature**: Quick preview on hover over file indicators
- **Full Management**: Complete file operations available in task detail/edit view
- **Preview Style**: Thumbnails for images, file type icons for documents, click to view larger/download

### File Type Support

- **Scope**: Accept any file type for maximum flexibility
- **Validation**: Must implement robust file type validation and security scanning
- **Security Considerations**: Virus scanning, executable file warnings, content type verification

### Storage & Infrastructure

- **Storage Method**: Local filesystem (simple, fast, no cloud dependencies)
- **File Size Limit**: 25MB per file (generous enough for documents, presentations, media)
- **Directory Structure**: Organize by user ID and task ID for easy access control
- **File Naming**: Generate unique filenames to prevent conflicts, preserve original names for display

### Security Model

- **Access Control**: Task-level access matching existing security (users only see files on their own tasks)
- **URL Security**: Private file URLs requiring authentication
- **File Isolation**: Each file scoped to specific task and user
- **Cleanup Policy**: Delete files immediately when parent task is deleted (clean, no orphaned files)

### Error Handling & Recovery

- **Validation**: Check file size and type before upload starts
- **Progress Feedback**: Inline error messages for specific upload failures
- **Recovery Options**: Allow retry for failed uploads due to network issues
- **Resume Capability**: Partial upload recovery for interrupted large file transfers
- **User Feedback**: Clear error messages (file too large, invalid type, network error, etc.)

### Technical Requirements

- **Database Schema**: FileAttachment model with task relation, metadata storage
- **Upload Endpoint**: Chunked upload support for large files and resume capability
- **File Serving**: Secure download endpoint with access control
- **Preview Generation**: Thumbnail creation for images, file type icon mapping
- **Cleanup Jobs**: Background task cleanup when tasks deleted

### User Experience Flow

1. **Upload**: Drag files onto task card or upload area in edit view
2. **Progress**: See upload progress with percentage and file names
3. **Display**: File count/thumbnails appear on task cards immediately
4. **Preview**: Hover over file indicators for quick preview
5. **Management**: Full CRUD operations in task detail view
6. **Download**: Click thumbnail/name to download or view larger

## Integration Points

### Existing Components

- **TaskCard**: Add file attachment indicators and hover preview
- **TaskForm**: Integrate drag & drop upload area
- **TaskList**: Show file counts without cluttering layout
- **Server Actions**: New uploadFiles, deleteFile, downloadFile actions

### Database Extensions

- Extend Task model relationship to FileAttachment
- File metadata tracking (original name, size, mime type, upload date)
- Efficient queries for task files and user file quotas

### API Considerations

- Chunked upload endpoints for large files
- Progress tracking for long uploads
- Proper MIME type detection and validation
- Rate limiting for upload endpoints

## Deferred Decisions

- Advanced preview (PDF viewer, document previews) → Phase 7 or v2
- File versioning → v2 Advanced File Management
- Batch file operations → v2 Advanced File Management
- File sharing between tasks → v2 Collaboration Features
- External cloud storage → v2 if local storage becomes limiting

## Success Criteria

1. Users can drag & drop files onto tasks
2. Upload progress is clearly visible with percentage
3. Failed uploads show clear error messages with retry options
4. File indicators appear on task cards immediately after upload
5. Hover previews work smoothly without layout shifts
6. File downloads work reliably with proper security
7. File cleanup happens automatically when tasks are deleted
8. System enforces 25MB file size limit with clear feedback
9. All file operations respect task ownership permissions
10. Large file uploads can be interrupted and resumed

---

*Context complete. Ready for research and planning phases.*
