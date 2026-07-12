








export function get_user_location({ high_acccuracy = false } = {}) {

    // get current user's location
    return new Promise((resolve, reject) => {
    navigator.geolocation.getCurrentPosition(
      resolve,
      reject, {
        enableHighAccuracy: high_acccuracy
      }
    );
  });

}