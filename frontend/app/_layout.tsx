import { useEffect, useState } from "react";
import { Stack } from "expo-router";
import { useFonts } from "expo-font";
import Splash from "../components/Splash";
import { UserProvider } from "../contexts/UserContext";

export default function Layout() {
  const [showSplash, setShowSplash] = useState(true);

  const [fontsLoaded] = useFonts({
    BubbleBobble: require("../assets/fonts/BubbleBobble-rg3rx.ttf"),
  });

  useEffect(() => {
    const timer = setTimeout(() => setShowSplash(false), 2000);
    return () => clearTimeout(timer);
  }, []);

  if (showSplash || !fontsLoaded) {
    return <Splash />;
  }

  return (
    <UserProvider>
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Screen name="index" />
        <Stack.Screen name="screens/recommend" />
        <Stack.Screen name="screens/model" />
        <Stack.Screen name="screens/profile" />
      </Stack>
    </UserProvider>
  );
}