import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.newsgap.app',
  appName: 'NewsGap',
  webDir: 'dist',
  server: {
    androidScheme: 'https'
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      backgroundColor: '#ffffff',
      showSpinner: false
    },
    CapacitorSQLite: {
      iosDatabaseLocation: 'Library/CapacitorDatabase',
      androidDatabaseLocation: 'default'
    }
  }
};

export default config;
