import React from 'react';
import { Bell, User, Search, FileText, BarChart3, MessagesSquare, Home, Menu, Settings } from 'lucide-react';
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useLocation, Link } from "react-router-dom";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const Header: React.FC = () => {
  const location = useLocation();
  
  const isActive = (path: string) => {
    return location.pathname === path;
  };
  
  return (
    <header className="bg-white border-b border-gray-200 py-4 px-6 sticky top-0 z-30">
      <div className="flex justify-between items-center">
        {/* Logo & Title */}
        <div className="flex items-center">
          <h1 className="text-xl font-semibold text-docflow-primary mr-2">DocDive</h1>
          <span className="text-xs bg-docflow-accent text-white px-2 py-0.5 rounded">Document Search and Q&A Platform</span>
        </div>
        
        {/* Navigation - Desktop */}
        <div className="hidden md:flex items-center space-x-8">
          <Link 
            to="/" 
            className={`flex items-center space-x-1 ${isActive('/') ? 'text-docflow-accent font-medium' : 'text-docflow-secondary hover:text-docflow-primary'}`}
          >
            <Home className="h-4 w-4" />
            <span>Dashboard</span>
          </Link>
          <Link 
            to="/documents" 
            className={`flex items-center space-x-1 ${isActive('/documents') ? 'text-docflow-accent font-medium' : 'text-docflow-secondary hover:text-docflow-primary'}`}
          >
            <FileText className="h-4 w-4" />
            <span>Documents</span>
          </Link>
          <Link 
            to="/query" 
            className={`flex items-center space-x-1 ${isActive('/query') ? 'text-docflow-accent font-medium' : 'text-docflow-secondary hover:text-docflow-primary'}`}
          >
            <MessagesSquare className="h-4 w-4" />
            <span>Q&A</span>
          </Link>
          <Link 
            to="/metrics" 
            className={`flex items-center space-x-1 ${isActive('/metrics') ? 'text-docflow-accent font-medium' : 'text-docflow-secondary hover:text-docflow-primary'}`}
          >
            <BarChart3 className="h-4 w-4" />
            <span>Metrics</span>
          </Link>
          <Link 
            to="/settings" 
            className={`flex items-center space-x-1 ${isActive('/settings') ? 'text-docflow-accent font-medium' : 'text-docflow-secondary hover:text-docflow-primary'}`}
          >
            <Settings className="h-4 w-4" />
            <span>Settings</span>
          </Link>
        </div>
        
        {/* Search Bar - Medium to large screens */}
        {/* <div className="hidden lg:block flex-1 max-w-md mx-6">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-docflow-secondary" />
            <Input 
              type="text" 
              placeholder="Search across documents..." 
              className="pl-9 bg-gray-50 border-gray-200 focus:bg-white"
            />
          </div>
        </div> */}
        
        {/* User Controls */}
        <div className="flex items-center space-x-4">
          {/* Mobile Navigation */}
          {/* <div className="md:hidden">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon">
                  <Menu className="h-5 w-5" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                <DropdownMenuItem asChild>
                  <Link to="/" className="flex items-center w-full">
                    <Home className="h-4 w-4 mr-2" />
                    Dashboard
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link to="/documents" className="flex items-center w-full">
                    <FileText className="h-4 w-4 mr-2" />
                    Documents
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link to="/query" className="flex items-center w-full">
                    <MessagesSquare className="h-4 w-4 mr-2" />
                    Q&A
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link to="/metrics" className="flex items-center w-full">
                    <BarChart3 className="h-4 w-4 mr-2" />
                    Metrics
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link to="/system" className="flex items-center w-full">
                    <Settings className="h-4 w-4 mr-2" />
                    System
                  </Link>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div> */}
          
          {/* Notifications */}
          {/* <button className="p-2 rounded-full hover:bg-gray-100 relative">
            <Bell className="h-5 w-5 text-docflow-secondary" />
            <span className="absolute top-1 right-1 h-2 w-2 bg-docflow-accent rounded-full"></span>
          </button> */}
          
          {/* User Menu */}
          {/* <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <div className="flex items-center space-x-2 cursor-pointer">
                <div className="w-8 h-8 bg-docflow-primary text-white rounded-full flex items-center justify-center">
                  <User className="h-4 w-4" />
                </div>
                <span className="text-sm font-medium hidden sm:block">Admin User</span>
              </div>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuLabel>My Account</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem>Profile</DropdownMenuItem>
              <DropdownMenuItem>Settings</DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem>Log out</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu> */}
        </div>
      </div>
      
      {/* Search Bar - Mobile */}
      {/* <div className="mt-3 lg:hidden">
        <div className="relative">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-docflow-secondary" />
          <Input 
            type="text" 
            placeholder="Search across documents..." 
            className="pl-9 bg-gray-50 border-gray-200 focus:bg-white"
          />
        </div>
      </div> */}
    </header>
  );
};

export default Header;
