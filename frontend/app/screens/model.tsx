// model.tsx
import React, { useEffect, useMemo, useRef } from "react";
import {
  StyleSheet,
  View,
  Text,
  Image,
  ImageBackground,
  TouchableOpacity,
  Animated,
  Dimensions,
} from "react-native";

const profilePic = require("../../assets/images/profile_pic.png");
const splashBg = require("../../assets/images/splash_bg.png");
const celebImage = require("../../assets/images/margo.jpg");

const { width: SCREEN_W, height: SCREEN_H } = Dimensions.get("window");

// --- Star and Animation Specs (Keep these for the star effect) ---
type StarSpec = {
  id: string;
  x: number;
  y: number;
  size: number;
  twinkleSpeed: number;
  moveRange: number;
};

const NUM_STARS = 36;
function rand(min: number, max: number) {
  return Math.random() * (max - min) + min;
}
// --- End Star and Animation Specs ---

// We only need the star animations, the glowAnim is no longer necessary.
export default function ModelScreen(): React.ReactElement {
  
  const stars = useMemo<StarSpec[]>(
    () =>
      Array.from({ length: NUM_STARS }).map(() => ({
        id: Math.random().toString(36).slice(2),
        x: rand(8, SCREEN_W - 8),
        y: rand(80, SCREEN_H - 120),
        size: Math.round(rand(8, 18)),
        twinkleSpeed: rand(900, 3000),
        moveRange: rand(2.5, 8),
      })),
    []
  );

  const starAnimsRef = useRef(
    stars.map(() => ({
      opacity: new Animated.Value(rand(0.2, 1)),
      scale: new Animated.Value(rand(0.6, 1.3)),
      translateY: new Animated.Value(0),
    }))
  );
  
  // NOTE: Removed glowAnim useRef here.

  useEffect(() => {
    // NOTE: Removed glow pulse animation here.

    // Start per-star animations (twinkle + tiny float)
    const starLoops = starAnimsRef.current.map((anim, i) => {
      const spec = stars[i];

      const twinkle = Animated.sequence([
        Animated.timing(anim.opacity, { toValue: rand(0.15, 1), duration: spec.twinkleSpeed, useNativeDriver: true }),
        Animated.timing(anim.opacity, { toValue: rand(0.15, 1), duration: spec.twinkleSpeed * 0.6, useNativeDriver: true }),
      ]);

      const scaleSeq = Animated.sequence([
        Animated.timing(anim.scale, { toValue: rand(0.7, 1.4), duration: spec.twinkleSpeed * 0.9, useNativeDriver: true }),
        Animated.timing(anim.scale, { toValue: rand(0.6, 1.0), duration: spec.twinkleSpeed * 0.7, useNativeDriver: true }),
      ]);

      const floatSeq = Animated.sequence([
        Animated.timing(anim.translateY, { toValue: -spec.moveRange, duration: spec.twinkleSpeed * 0.9, useNativeDriver: true }),
        Animated.timing(anim.translateY, { toValue: spec.moveRange * 0.6, duration: spec.twinkleSpeed * 0.8, useNativeDriver: true }),
      ]);

      const combined = Animated.parallel([twinkle, scaleSeq, floatSeq]);
      const delayed = Animated.sequence([Animated.delay(Math.floor(rand(0, 800))), Animated.loop(combined)]);
      return delayed;
    });

    Animated.stagger(80, starLoops).start();

  }, [stars]); // Removed glowAnim from dependency array

  const containerWidth = SCREEN_W * 0.85; 

  // NOTE: Removed glowScale and glowOpacity interpolations here.

  return (
    <ImageBackground source={splashBg} style={styles.background}>
      
      {/* Background elements (Stars) */}
      <View style={[StyleSheet.absoluteFill, styles.centerAll, { zIndex: 1 }]} pointerEvents="none">
        {stars.map((s, i) => {
          const anim = starAnimsRef.current[i];
          return (
            <Animated.Text
              key={s.id}
              style={[
                styles.star,
                {
                  left: s.x - s.size / 2,
                  top: s.y - s.size / 2,
                  fontSize: s.size,
                  opacity: anim.opacity,
                  transform: [{ translateY: anim.translateY }, { scale: anim.scale }],
                },
              ]}
            >
              ✦
            </Animated.Text>
          );
        })}
      </View>
      
      {/* Main Content Area (No glow wrapper needed now) */}
      <View style={styles.scrollContentContainer}>
        
        {/* Profile Picture (Stays absolute) */}
        <View style={styles.topRightProfile}>
          <TouchableOpacity onPress={() => console.log("Profile pressed")} style={styles.profileContainer}>
            <View style={styles.profilePicBorder}>
              <Image source={profilePic} style={styles.profilePic} />
            </View>
          </TouchableOpacity>
        </View>

        {/* White rounded celeb container (The Card itself) */}
        {/* NOTE: Removed the contentAndGlowWrapper, containerBox now gets the marginTop */}
        <View style={[styles.containerBox, { width: containerWidth }]}>
            
            {/* Celeb Image (Now smaller and contained, centered) */}
            <View style={styles.imageWrapper}>
                <Image source={celebImage} style={styles.celebImage} />
            </View>
            
            {/* Text at the bottom of the white card */}
            <Text style={styles.celebText}>Your Celeb Twin ✨</Text>
        </View>
        
        {/* Spacer to push content up and center it visually */}
        <View style={styles.spacer} />
        
        {/* SAMSUNG PRISM text at the bottom */}
        <Text style={styles.samsungPrismText}>SAMSUNG PRISM</Text>
      </View>
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  background: {
    flex: 1,
    resizeMode: "cover",
  },
  
  scrollContentContainer: {
    flexGrow: 1,
    justifyContent: 'center', 
    alignItems: 'center',
    paddingVertical: 40,
    width: '100%',
    position: 'relative', 
  },
  
  topRightProfile: {
    position: 'absolute',
    top: 70, 
    right: 20,
    alignItems: 'center',
    zIndex: 10,
  },
  profileContainer: {
    alignItems: "center",
  },
  profilePicBorder: {
    width: 80,
    height: 80,
    borderRadius: 40,
    borderWidth: 1,
    borderColor: "#e68998",
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#FFF",
  },
  profilePic: {
    width: 70,
    height: 70,
    borderRadius: 35,
    resizeMode: "cover",
  },

  // White Card Container - Restored marginTop here
  containerBox: {
    backgroundColor: "#fff",
    borderRadius: 22,
    padding: 18, 
    alignItems: "center",
    maxWidth: 360,
    marginTop: 150, // CRITICAL: Positions the card below the profile pic
    shadowColor: "#e68998",
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.18,
    shadowRadius: 18,
    elevation: 12,
    position: 'relative', 
    zIndex: 2, 
  },
  
  // Wrapper for the image to control its size relative to the card
  imageWrapper: {
    width: '100%', 
    aspectRatio: 0.8, 
    borderRadius: 16, 
    overflow: 'hidden', 
    marginBottom: 10,
    alignItems: 'center', 
    justifyContent: 'center', 
  },

  celebImage: {
    width: "100%",
    height: "100%",
    resizeMode: "contain", // Ensures the entire image is visible
  },

  celebText: {
    fontSize: 20,
    fontWeight: "700",
    color: "#333",
    textAlign: "center",
    paddingBottom: 5, 
  },

  samsungPrismText: {
    position: 'absolute', 
    bottom: 20,
    fontSize: 18.5,
    color: '#ffffff',
    letterSpacing: 1,
  },
  
  spacer: {
    height: 60, 
  },

  // Star Styles 
  centerAll: { justifyContent: "center", alignItems: "center" },
  star: { position: "absolute", color: "#fff", textShadowColor: "rgba(255, 180, 200, 0.9)", textShadowOffset: { width: 0, height: 0 }, textShadowRadius: 6, transform: [{ rotate: "0deg" }] },
  
  // NOTE: All glowCircle/glowCircleInner styles have been removed.
});