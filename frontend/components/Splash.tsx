import { View, Text, StyleSheet, Image } from "react-native";

export default function Splash() {
  return (
    <View style={styles.container}>
      <Image source={require("../assets/dress_icon.png")} style={styles.image} />
      <Text style={styles.text}>Style Sense AI</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#E75480",
    justifyContent: "center",
    alignItems: "center",
  },
  image: {
    width: 150,
    height: 150,
    marginBottom: 20,
  },
  text: {
    fontSize: 28,
    fontWeight: "bold",
    color: "white",
  },
});
