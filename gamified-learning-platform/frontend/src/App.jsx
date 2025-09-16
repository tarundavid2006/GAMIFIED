import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Toaster } from 'react-hot-toast'

// Components
import LoadingScreen from './components/LoadingScreen'
import AvatarSelection from './components/AvatarSelection'
import MainLayout from './components/MainLayout'
import HomePage from './pages/HomePage'
import SubjectPage from './pages/SubjectPage'
import LevelPage from './pages/LevelPage'
import RewardsPage from './pages/RewardsPage'
import ProfilePage from './pages/ProfilePage'

// Services and Hooks
import { useOfflineStorage } from './hooks/useOfflineStorage'
import { useDeviceProfile } from './hooks/useDeviceProfile'
import { usePWA } from './hooks/usePWA'
import { initializeAudio } from './services/audioService'

// Styles
import './App.css'

function App() {
  const [isLoading, setIsLoading] = useState(true)
  const [showAvatarSelection, setShowAvatarSelection] = useState(false)
  
  // Initialize offline storage and device profile
  const { isReady: storageReady, syncStatus } = useOfflineStorage()
  const { 
    currentProfile, 
    avatars, 
    setCurrentAvatar, 
    isProfileReady 
  } = useDeviceProfile()
  
  // PWA installation
  const { canInstall, installApp } = usePWA()
  
  useEffect(() => {
    const initializeApp = async () => {
      try {
        // Wait for storage to be ready
        if (!storageReady) return
        
        // Initialize audio system
        await initializeAudio()
        
        // Check if user needs to select avatar
        if (!currentProfile?.avatar && avatars.length > 0) {
          setShowAvatarSelection(true)
        }
        
        // App is ready
        setIsLoading(false)
      } catch (error) {
        console.error('Failed to initialize app:', error)
        setIsLoading(false)
      }
    }
    
    initializeApp()
  }, [storageReady, currentProfile, avatars])
  
  // Handle avatar selection
  const handleAvatarSelected = (avatar) => {
    setCurrentAvatar(avatar.id)
    setShowAvatarSelection(false)
  }
  
  // Show loading screen
  if (isLoading || !storageReady || !isProfileReady) {
    return <LoadingScreen />
  }
  
  // Show avatar selection screen
  if (showAvatarSelection) {
    return (
      <AvatarSelection 
        avatars={avatars}
        onAvatarSelected={handleAvatarSelected}
        canSkip={!!currentProfile?.avatar}
        onSkip={() => setShowAvatarSelection(false)}
      />
    )
  }
  
  return (
    <Router>
      <div className="app">
        {/* Background gradient */}
        <div className="fixed inset-0 bg-gradient-to-br from-blue-400 via-purple-500 to-pink-500 -z-10" />
        
        {/* PWA Install Prompt */}
        {canInstall && (
          <motion.div
            initial={{ y: -100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="fixed top-4 left-4 right-4 bg-white rounded-lg p-4 shadow-lg z-50"
          >
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-bold text-gray-900">Install App</h3>
                <p className="text-sm text-gray-600">
                  Install for better offline experience!
                </p>
              </div>
              <button
                onClick={installApp}
                className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors"
              >
                Install
              </button>
            </div>
          </motion.div>
        )}
        
        {/* Sync Status Indicator */}
        {syncStatus && syncStatus !== 'idle' && (
          <motion.div
            initial={{ x: 100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            className="fixed top-4 right-4 bg-white rounded-lg p-3 shadow-lg z-40"
          >
            <div className="flex items-center space-x-2">
              {syncStatus === 'syncing' && (
                <>
                  <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse" />
                  <span className="text-sm text-gray-700">Syncing...</span>
                </>
              )}
              {syncStatus === 'offline' && (
                <>
                  <div className="w-3 h-3 bg-orange-500 rounded-full" />
                  <span className="text-sm text-gray-700">Offline</span>
                </>
              )}
              {syncStatus === 'error' && (
                <>
                  <div className="w-3 h-3 bg-red-500 rounded-full" />
                  <span className="text-sm text-gray-700">Sync Error</span>
                </>
              )}
            </div>
          </motion.div>
        )}
        
        {/* Main App Routes */}
        <AnimatePresence mode="wait">
          <Routes>
            <Route path="/" element={<MainLayout />}>
              <Route index element={<HomePage />} />
              <Route path="subjects/:subjectSlug" element={<SubjectPage />} />
              <Route path="levels/:levelId" element={<LevelPage />} />
              <Route path="rewards" element={<RewardsPage />} />
              <Route path="profile" element={<ProfilePage />} />
              <Route 
                path="avatar-selection" 
                element={
                  <AvatarSelection 
                    avatars={avatars}
                    onAvatarSelected={handleAvatarSelected}
                    canSkip={true}
                    onSkip={() => window.history.back()}
                  />
                } 
              />
            </Route>
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AnimatePresence>
        
        {/* Toast Notifications */}
        <Toaster
          position="bottom-center"
          toastOptions={{
            duration: 3000,
            style: {
              background: '#363636',
              color: '#fff',
              borderRadius: '12px',
              fontSize: '14px',
              fontWeight: '500'
            },
            success: {
              iconTheme: {
                primary: '#10B981',
                secondary: '#fff'
              }
            },
            error: {
              iconTheme: {
                primary: '#EF4444',
                secondary: '#fff'
              }
            }
          }}
        />
      </div>
    </Router>
  )
}

export default App