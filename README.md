## audio-gorilla

# Fake API Details
-All APIs have documentation under the method. This is used by the model to see the different
method signatures and method outputs, and how to combine them.
-Some APIs are either taken inspiration directly from the source (e.g, google drive) or are taken inspiration from other research (AppWorld)
-All of the APIs don't have the whole breadth of fake methods that could've been taken from the source/inspiration, and that is because we want to take ones that use core funcitonality
-Some APIs are stateful and others are not. The decision was based on the source/inspiration. The stateful APIs are: GoogleCalendarApis, GoogleDriveApis, GmailApis, SpotifyApis, YouTubeApis, XApis, TeslaFleetApis, and VenmoApis; The stateless APIs are: AmazonApis, SmartThingsApis, SimpleNoteApis, and CommunilinkApis.
--In our case, for statelful: you authenticate once and then all requests are remembered to that user
--In our case, for stateless: you pass user context w/ each call
--There are pros and cons to stateless and stateful for model testing; Pros (for stateless): the model can switch users instantly w/o auth, can act as multiple users in parallel, no sessio state to manage, and it's a more deterministic behavior. However, the stateful design is more realistic for modern APIs
-