from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel

class Location(BaseModel):
    """Model for group location."""
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    zipcode: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    virtualMeetingLink: Optional[str] = None

class StudyPlan(BaseModel):
    """Model for a study plan."""
    id: str # This ID is within the JSONB array, usually string-based or unique within array
    title: str
    description: str
    createdAt: datetime

class Meal(BaseModel):
    """Model for a meal."""
    id: str # This ID is within the JSONB array
    mealName: str
    description: str
    createdAt: datetime

class GroupMember(BaseModel):
    """Model for a group member."""
    userId: str  # UUID public_id
    username: str
    email: str
    portraitUrl: Optional[str] = None
    role: str
    joinedAt: datetime

class GroupRequest(BaseModel):
    """Model for a group request."""
    id: int
    groupId: str  # UUID public_id
    userId: str  # UUID public_id
    username: Optional[str] = None
    requestMessage: str
    createdAt: datetime
    status: Optional[str] = "pending"  # pending, approved, rejected

class ChatMessage(BaseModel):
    """Model for a chat message."""
    id: int
    userId: str  # UUID public_id
    username: str
    message: str
    sentAt: datetime

class Group(BaseModel):
    """Model for a group."""
    public_id: str  # UUID (public-facing)
    name: str
    description: str
    leaderUserId: str  # UUID public_id
    location: Location
    image: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime

# Request Models
class CreateGroupRequest(BaseModel):
    """Model for creating a new group."""
    name: str
    description: str
    leaderUserId: str  # public_id (UUID) of the leader
    location: Location
    image: Optional[str] = None

class InitializeGroupRequest(BaseModel):
    """Model for initializing a group."""
    groupPublicId: str  # UUID public_id

class GetUsersRequest(BaseModel):
    """Model for getting group users."""
    groupPublicId: str  # UUID public_id

class GetChatRequest(BaseModel):
    """Model for getting group chat."""
    groupPublicId: str  # UUID public_id

class GetMealsRequest(BaseModel):
    """Model for getting group meals."""
    groupPublicId: str  # UUID public_id

class GetStudyPlanRequest(BaseModel):
    """Model for getting group study plans."""
    groupPublicId: str  # UUID public_id

# Response Models
class CreateGroupResponse(BaseModel):
    """Model for create group response."""
    success: bool
    message: str
    groupPublicId: Optional[str] = None  # UUID public_id

class InitializeGroupResponse(BaseModel):
    """Model for initialize group response."""
    success: bool
    message: str

class GetUsersResponse(BaseModel):
    """Model for get users response."""
    success: bool
    message: str
    users: List[GroupMember] = []
    memberCount: int = 0

class GetGroupChatResponse(BaseModel):
    """Model for get chat response."""
    success: bool
    message: str
    messages: List[ChatMessage] = []

class GetMealsResponse(BaseModel):
    """Model for get meals response."""
    success: bool
    message: str
    meals: List[Meal] = []

class GetStudyPlanResponse(BaseModel):
    """Model for get study plans response."""
    success: bool
    message: str
    studyPlans: List[StudyPlan] = []

class GetGroupsResponse(BaseModel):
    """Model for get groups response."""
    success: bool
    message: str
    groups: List[Group] = []

class GetGroupResponse(BaseModel):
    """Model for get single group response."""
    success: bool
    message: str
    group: Optional[Group] = None

class Worksheet(BaseModel):
    """Model for a Bible worksheet."""
    id: int
    groupPublicId: str  # UUID public_id
    title: str
    content: str
    createdAt: datetime
    updatedAt: datetime

class CreateGroupChatRequest(BaseModel):
    """Model for creating a group chat message."""
    groupPublicId: str  # UUID public_id
    userPublicId: str  # UUID public_id
    message: str

class CreateGroupChatResponse(BaseModel):
    """Model for create group chat response."""
    success: bool
    message: str
    chatId: Optional[int] = None

class CreateWorksheetRequest(BaseModel):
    """Model for creating a Bible worksheet."""
    groupPublicId: str  # UUID public_id
    title: str
    content: str

class CreateWorksheetResponse(BaseModel):
    """Model for create worksheet response."""
    success: bool
    message: str
    worksheetId: Optional[int] = None

class GetWorksheetsRequest(BaseModel):
    """Model for getting group worksheets."""
    groupPublicId: str  # UUID public_id

class GetWorksheetsResponse(BaseModel):
    """Model for get worksheets response."""
    success: bool
    message: str
    worksheets: List[Worksheet] = []

class AddGroupMemberRequest(BaseModel):
    """Model for adding a group member."""
    groupPublicId: str  # UUID public_id
    userPublicId: str  # UUID public_id

class AddGroupMemberResponse(BaseModel):
    """Model for add group member response."""
    success: bool
    message: str

class RemoveGroupMemberRequest(BaseModel):  
    """Model for removing a group member."""
    groupPublicId: str  # UUID public_id
    userPublicId: str  # UUID public_id

class RemoveGroupMemberResponse(BaseModel):
    """Model for remove group member response."""
    success: bool
    message: str

class UpdateGroupMemberRequest(BaseModel):
    """Model for updating a group member."""
    groupPublicId: str  # UUID public_id
    userPublicId: str  # UUID public_id
    role: str

class UpdateGroupMemberResponse(BaseModel):
    """Model for update group member response."""
    success: bool
    message: str

class GetGroupMembersRequest(BaseModel):
    """Model for getting group members."""
    groupPublicId: str  # UUID public_id

class GetGroupMembersResponse(BaseModel):
    """Model for get group members response."""
    success: bool
    message: str
    members: List[GroupMember] = []
    memberCount: int = 0

class GetGroupMemberRequest(BaseModel):
    """Model for getting a group member."""
    groupPublicId: str  # UUID public_id
    userPublicId: str  # UUID public_id

class GetGroupMemberResponse(BaseModel):
    """Model for get group member response."""
    success: bool
    message: str
    member: GroupMember

class JoinGroupRequest(BaseModel):
    """Model for joining a group."""
    groupPublicId: str  # UUID public_id
    userPublicId: str  # UUID public_id

class JoinGroupResponse(BaseModel):
    """Model for join group response."""
    success: bool
    message: str

class LeaveGroupRequest(BaseModel):
    """Model for leaving a group."""
    groupPublicId: str  # UUID public_id
    userPublicId: str  # UUID public_id

class LeaveGroupResponse(BaseModel):
    """Model for leave group response."""
    success: bool
    message: str

class CreateGroupRequestRequest(BaseModel):
    """Model for creating a group request."""
    groupPublicId: str  # UUID public_id
    userPublicId: str  # UUID public_id
    requestMessage: Optional[str] = ""

class CreateGroupRequestResponse(BaseModel):
    """Model for create group request response."""
    success: bool
    message: str
    requestId: Optional[int] = None

class GetGroupRequestsRequest(BaseModel):
    """Model for getting group requests."""
    groupPublicId: str  # UUID public_id

class GetGroupRequestsResponse(BaseModel):
    """Model for get group requests response."""
    success: bool
    message: str
    requests: List[GroupRequest] = []

class GroupRoleConfig(BaseModel):
    """Model for a group role configuration."""
    id: int
    groupPublicId: str  # UUID public_id
    roleName: str
    permissions: List[str]
    createdAt: datetime
    updatedAt: datetime

class CreateGroupRoleConfigRequest(BaseModel):
    """Model for creating a group role configuration."""
    groupPublicId: str  # UUID public_id
    roleName: str
    permissions: List[str]

class CreateGroupRoleConfigResponse(BaseModel):
    """Model for create group role config response."""
    success: bool
    message: str
    groupRoleId: Optional[int] = None

class GetGroupRoleConfigsRequest(BaseModel):
    """Model for getting group role configs."""
    groupPublicId: str  # UUID public_id

class GetGroupRoleConfigsResponse(BaseModel):
    """Model for get group role configs response."""
    success: bool
    message: str
    roleConfigs: List[GroupRoleConfig] = []

class UpdateGroupRoleConfigRequest(BaseModel):
    """Model for updating a group role configuration."""
    groupPublicId: str  # UUID public_id
    roleName: str
    permissions: List[str]

class UpdateGroupRoleConfigResponse(BaseModel):
    """Model for update group role config response."""
    success: bool
    message: str

class DeleteGroupRoleConfigRequest(BaseModel):
    """Model for deleting a group role configuration."""
    groupPublicId: str  # UUID public_id
    roleName: str

class DeleteGroupRoleConfigResponse(BaseModel):
    """Model for delete group role config response."""
    success: bool
    message: str

class UploadWorksheetResponse(BaseModel):
    """Model for upload worksheet response."""
    success: bool
    message: str
    worksheetId: Optional[int] = None
    fileId: Optional[int] = None
    fileName: Optional[str] = None
    fileType: Optional[str] = None

class CreateWorksheetTextRequest(BaseModel):
    """Model for create worksheet text request."""
    groupPublicId: str  # UUID public_id
    title: str
    content: str

class CreateWorksheetTextResponse(BaseModel):
    """Model for create worksheet text response."""
    success: bool
    message: str
    worksheetId: Optional[int] = None
