import { useEffect, useState } from "react";
import { Stack } from "expo-router";
import { useFonts } from "expo-font";
import Splash from "../components/Splash";

export default function Layout() {
  const [showSplash, setShowSplash] = useState(true);

  const [fontsLoaded] = useFonts({
    BubbleBobble: require("../assets/fonts/BubbleBobble-rg3rx.ttf"),
  });

  const [fontsLoaded] = useFonts({
    BubbleBobble: require("../assets/fonts/BubbleBobble-rg3rx.ttf"),
  });

  useEffect(() => {
    const timer = setTimeout(() => setShowSplash(false), 2000);
    return () => clearTimeout(timer);
  }, []);

  if (showSplash) {
    return <Splash />;
  }

  return showSplash ? (
    <Splash />
  ) : (
  return showSplash ? (
    <Splash />
  ) : (
    <Stack screenOptions={{ headerShown: false }}>
      <Stack.Screen name="index" />
    </Stack>
  );
}