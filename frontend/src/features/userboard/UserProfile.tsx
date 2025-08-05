import React, { useState } from 'react';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { Separator } from '../../components/ui/separator';
import { Badge } from '../../components/ui/badge';
import {
    User,
    Mail,
    Phone,
    CreditCard,
    Settings,
    Shield,
    Calendar,
    CheckCircle,
    AlertCircle,
    ArrowLeft
} from 'lucide-react';
import { Link } from 'react-router-dom';

interface UserProfileProps {
    user: any;
    onLogout: () => void;
}

export function UserProfile({ user, onLogout }: UserProfileProps) {
    const [isEditing, setIsEditing] = useState(false);
    const [profileData, setProfileData] = useState({
        username: user?.username || '',
        email: user?.email || '',
        phone: user?.phone || '',
        firstName: user?.firstName || '',
        lastName: user?.lastName || ''
    });

    const handleSave = () => {
        // TODO: Implement API call to update user profile
        setIsEditing(false);
    };

    const handleCancel = () => {
        setProfileData({
            username: user?.username || '',
            email: user?.email || '',
            phone: user?.phone || '',
            firstName: user?.firstName || '',
            lastName: user?.lastName || ''
        });
        setIsEditing(false);
    };

    return (
        <div className="container mx-auto px-4 py-8 max-w-4xl">
            {/* Header */}
            <div className="flex items-center space-x-4 mb-8">
                <Link to="/userboard">
                    <Button variant="ghost" size="sm">
                        <ArrowLeft className="h-4 w-4 mr-2" />
                        Back to Dashboard
                    </Button>
                </Link>
                <div>
                    <h1 className="text-3xl font-bold">Profile Settings</h1>
                    <p className="text-muted-foreground">Manage your account settings and preferences</p>
                </div>
            </div>

            <Tabs defaultValue="profile" className="space-y-6">
                <TabsList className="grid w-full grid-cols-4">
                    <TabsTrigger value="profile">Profile</TabsTrigger>
                    <TabsTrigger value="billing">Billing</TabsTrigger>
                    <TabsTrigger value="security">Security</TabsTrigger>
                    <TabsTrigger value="preferences">Preferences</TabsTrigger>
                </TabsList>

                {/* Profile Tab */}
                <TabsContent value="profile" className="space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center space-x-2">
                                <User className="h-5 w-5" />
                                <span>Personal Information</span>
                            </CardTitle>
                            <CardDescription>
                                Update your personal details and contact information
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div className="space-y-2">
                                    <Label htmlFor="firstName">First Name</Label>
                                    <Input
                                        id="firstName"
                                        value={profileData.firstName}
                                        onChange={(e) => setProfileData({ ...profileData, firstName: e.target.value })}
                                        disabled={!isEditing}
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="lastName">Last Name</Label>
                                    <Input
                                        id="lastName"
                                        value={profileData.lastName}
                                        onChange={(e) => setProfileData({ ...profileData, lastName: e.target.value })}
                                        disabled={!isEditing}
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="username">Username</Label>
                                    <Input
                                        id="username"
                                        value={profileData.username}
                                        onChange={(e) => setProfileData({ ...profileData, username: e.target.value })}
                                        disabled={!isEditing}
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="email">Email</Label>
                                    <div className="flex items-center space-x-2">
                                        <Input
                                            id="email"
                                            type="email"
                                            value={profileData.email}
                                            onChange={(e) => setProfileData({ ...profileData, email: e.target.value })}
                                            disabled={!isEditing}
                                        />
                                        <Badge variant="secondary">Verified</Badge>
                                    </div>
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="phone">Phone Number</Label>
                                    <Input
                                        id="phone"
                                        type="tel"
                                        value={profileData.phone}
                                        onChange={(e) => setProfileData({ ...profileData, phone: e.target.value })}
                                        disabled={!isEditing}
                                        placeholder="+1 (555) 123-4567"
                                    />
                                </div>
                            </div>

                            <div className="flex space-x-2">
                                {!isEditing ? (
                                    <Button onClick={() => setIsEditing(true)}>
                                        <Settings className="h-4 w-4 mr-2" />
                                        Edit Profile
                                    </Button>
                                ) : (
                                    <>
                                        <Button onClick={handleSave}>
                                            <CheckCircle className="h-4 w-4 mr-2" />
                                            Save Changes
                                        </Button>
                                        <Button variant="outline" onClick={handleCancel}>
                                            Cancel
                                        </Button>
                                    </>
                                )}
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Billing Tab */}
                <TabsContent value="billing" className="space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center space-x-2">
                                <CreditCard className="h-5 w-5" />
                                <span>Billing & Subscription</span>
                            </CardTitle>
                            <CardDescription>
                                Manage your subscription and payment methods
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            {/* Current Plan */}
                            <div className="border rounded-lg p-4">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <h3 className="font-semibold">Current Plan</h3>
                                        <p className="text-sm text-muted-foreground">Pro Plan - $29/month</p>
                                    </div>
                                    <Badge variant="default">Active</Badge>
                                </div>
                                <div className="mt-4 text-sm text-muted-foreground">
                                    <p>Next billing date: January 15, 2024</p>
                                    <p>Usage: 85% of monthly limit</p>
                                </div>
                            </div>

                            {/* Payment Methods */}
                            <div>
                                <h3 className="font-semibold mb-4">Payment Methods</h3>
                                <div className="space-y-3">
                                    <div className="flex items-center justify-between p-3 border rounded-lg">
                                        <div className="flex items-center space-x-3">
                                            <CreditCard className="h-5 w-5 text-muted-foreground" />
                                            <div>
                                                <p className="font-medium">•••• •••• •••• 4242</p>
                                                <p className="text-sm text-muted-foreground">Expires 12/25</p>
                                            </div>
                                        </div>
                                        <Badge variant="secondary">Default</Badge>
                                    </div>
                                </div>
                                <Button variant="outline" className="mt-4">
                                    <CreditCard className="h-4 w-4 mr-2" />
                                    Add Payment Method
                                </Button>
                            </div>

                            {/* Billing History */}
                            <div>
                                <h3 className="font-semibold mb-4">Billing History</h3>
                                <div className="space-y-2">
                                    <div className="flex items-center justify-between p-3 border rounded-lg">
                                        <div>
                                            <p className="font-medium">December 2023</p>
                                            <p className="text-sm text-muted-foreground">Pro Plan</p>
                                        </div>
                                        <div className="text-right">
                                            <p className="font-medium">$29.00</p>
                                            <p className="text-sm text-muted-foreground">Paid</p>
                                        </div>
                                    </div>
                                    <div className="flex items-center justify-between p-3 border rounded-lg">
                                        <div>
                                            <p className="font-medium">November 2023</p>
                                            <p className="text-sm text-muted-foreground">Pro Plan</p>
                                        </div>
                                        <div className="text-right">
                                            <p className="font-medium">$29.00</p>
                                            <p className="text-sm text-muted-foreground">Paid</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Security Tab */}
                <TabsContent value="security" className="space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center space-x-2">
                                <Shield className="h-5 w-5" />
                                <span>Security Settings</span>
                            </CardTitle>
                            <CardDescription>
                                Manage your account security and privacy
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            <div className="space-y-4">
                                <div className="flex items-center justify-between p-4 border rounded-lg">
                                    <div>
                                        <h3 className="font-semibold">Change Password</h3>
                                        <p className="text-sm text-muted-foreground">Last changed 30 days ago</p>
                                    </div>
                                    <Button variant="outline">Update</Button>
                                </div>

                                <div className="flex items-center justify-between p-4 border rounded-lg">
                                    <div>
                                        <h3 className="font-semibold">Two-Factor Authentication</h3>
                                        <p className="text-sm text-muted-foreground">Add an extra layer of security</p>
                                    </div>
                                    <Button variant="outline">Enable</Button>
                                </div>

                                <div className="flex items-center justify-between p-4 border rounded-lg">
                                    <div>
                                        <h3 className="font-semibold">Login Sessions</h3>
                                        <p className="text-sm text-muted-foreground">Manage active sessions</p>
                                    </div>
                                    <Button variant="outline">View</Button>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Preferences Tab */}
                <TabsContent value="preferences" className="space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center space-x-2">
                                <Settings className="h-5 w-5" />
                                <span>Preferences</span>
                            </CardTitle>
                            <CardDescription>
                                Customize your experience and notifications
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            <div className="space-y-4">
                                <div className="flex items-center justify-between p-4 border rounded-lg">
                                    <div>
                                        <h3 className="font-semibold">Email Notifications</h3>
                                        <p className="text-sm text-muted-foreground">Receive updates about your account</p>
                                    </div>
                                    <Button variant="outline">Configure</Button>
                                </div>

                                <div className="flex items-center justify-between p-4 border rounded-lg">
                                    <div>
                                        <h3 className="font-semibold">Theme</h3>
                                        <p className="text-sm text-muted-foreground">Choose your preferred appearance</p>
                                    </div>
                                    <Button variant="outline">Customize</Button>
                                </div>

                                <div className="flex items-center justify-between p-4 border rounded-lg">
                                    <div>
                                        <h3 className="font-semibold">Language</h3>
                                        <p className="text-sm text-muted-foreground">Select your preferred language</p>
                                    </div>
                                    <Button variant="outline">Change</Button>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    );
} 