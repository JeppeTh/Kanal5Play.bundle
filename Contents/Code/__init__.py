TITLE  = 'Kanal 5 Play'
ART    = 'art-default.jpg'
ICON   = 'icon-default.png'
PREFIX = '/video/kanal5'

BASE_URL        = 'http://www.kanal%splay.se'
API_URL         = BASE_URL + '/api'
START_URL       = API_URL + '/getMobileStartContent?format=FLASH'
PROGRAMS_URL    = API_URL + '/getMobileFindProgramsContent'
LIVE_EVENTS_URL = API_URL + '/live/getCurrentEvents'

GetShows           = SharedCodeService.kanal5lib.GetShows
GetEpisodes        = SharedCodeService.kanal5lib.GetEpisodes
ShowSeasons        = SharedCodeService.kanal5lib.ShowSeasons
ProgramShowMenu    = SharedCodeService.kanal5lib.ProgramShowMenu
Clips              = SharedCodeService.kanal5lib.Clips
GetNoShowContainer = SharedCodeService.kanal5lib.GetNoShowContainer
CHANNEL_LIST       = SharedCodeService.kanal5lib.CHANNEL_LIST

####################################################################################################
def Start():
    ObjectContainer.art = R(ART)
    HTTP.CacheTime      = CACHE_1HOUR 

####################################################################################################
@handler(PREFIX, TITLE, art = ART)
def MainMenu():

    oc = ObjectContainer(title1 = TITLE)

    oc.add(DirectoryObject(
            key   = Callback(PopularShows, title=unicode("Populära program")),
            title = unicode("Populära program"),
            thumb = R(ICON)
            )
           )
    
    oc.add(DirectoryObject(
            key   = Callback(LatestVideos, title=unicode("Senast tillagt")),
            title = unicode("Senast tillagt"),
            thumb = R(ICON)
            )
           )
    
    oc.add(DirectoryObject(
            key   = Callback(AllShows, title=unicode("Alla program")),
            title = unicode("Alla program"),
            thumb = R(ICON)
            )
           )
    
    oc.add(DirectoryObject(
            key   = Callback(Live, title=unicode("Live")),
            title = unicode("Live"),
            thumb = R(ICON)
            )
           )

    oc.add(SearchDirectoryObject(
            identifier = 'com.plexapp.plugins.kanal5play',
            title      = unicode('Sök'),
            summary    = unicode('Sök efter program och klipp på Kanal 5/9/11 Play'),
            prompt     = unicode('Sök på Kanal 5/9/11 Play'),
            thumb      = R('ikon-sok.png')
            )
           )
    return oc

####################################################################################################
@route(PREFIX + '/live')
def Live(title):
    oc   = ObjectContainer(title2 = unicode(title))

    for channelNo in CHANNEL_LIST:
        oc = AddLiveShows(oc, channelNo)

    if len(oc) < 1:
        oc = GetNoShowContainer(oc)

    return oc

def AddLiveShows(oc, channelNo):

    data = JSON.ObjectFromURL(LIVE_EVENTS_URL % channelNo, cacheTime = 0)

    for event in data['liveEvents']:
        if 'liveStreamingParams' in event:
            oc.add(
                CreateVideoClipObject(
                    url = event['liveStreamingParams']['streams'][0]['source'],
                    title = unicode(event['title'].strip()), 
                    thumb = event['photoUrl'],
                    desc = unicode(event['description'].strip())
                )
            )

    return oc 

####################################################################################################
@route(PREFIX + '/popularshows')
def PopularShows(title):
    oc   = ObjectContainer(title2 = unicode(title))

    for channelNo in CHANNEL_LIST:
        oc = AddPopularShows(oc, channelNo, len(oc) > 0)

    if len(oc) < 1:
        oc = GetNoShowContainer(oc)

    return oc

def AddPopularShows(oc, channelNo, checkDuplicates):
    data = JSON.ObjectFromURL(START_URL % channelNo)
    return GetShows(oc, data['hottestPrograms'], channelNo, checkDuplicates)

####################################################################################################
@route(PREFIX + '/latestvideos')
def LatestVideos(title):

    oc  = ObjectContainer(title2=unicode(title))

    for channelNo in CHANNEL_LIST:
        oc = AddLatestVideos(oc, channelNo)

    return oc

def AddLatestVideos(oc, channelNo):
    data = JSON.ObjectFromURL(START_URL % channelNo)

    return GetEpisodes(oc, data['newEpisodeVideos'], channelNo, sort='latest', filterClips=False)

####################################################################################################
@route(PREFIX + '/shows')
def AllShows(title):

    oc = ObjectContainer(title2=unicode(title))
    for channelNo in CHANNEL_LIST:
        oc = AddShows(oc, channelNo, len(oc) > 0)

    if len(oc) < 1:
        oc = GetNoShowContainer(oc)
    else:
        oc.objects.sort(key = lambda obj: obj.title)

    return oc

def AddShows(oc, channelNo, checkDuplicates):
    data = JSON.ObjectFromURL(PROGRAMS_URL % channelNo)
    return GetShows(oc, data['programsWithTemperatures'], channelNo, checkDuplicates)

####################################################################################################
@route(PREFIX + '/createvideoclipobject')
def CreateVideoClipObject(url, title, thumb, desc, include_container=False):

  videoclip_obj = VideoClipObject(
      key = Callback(CreateVideoClipObject, url=url, title=title, thumb=thumb, desc=desc, include_container=True),
      rating_key = url,
      title = title,
      thumb = thumb,
      summary = desc,
      items = [
        MediaObject(
          parts = [
            PartObject(key=HTTPLiveStreamURL(url))
          ],
          video_resolution = 'sd',
          audio_channels = 2,
          optimized_for_streaming = True
        )
      ]
  )

  if include_container:
      return ObjectContainer(objects=[videoclip_obj])
  else:
      return videoclip_obj
