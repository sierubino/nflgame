from nflgame import OrderedDict
import nflgame.statmap


class PlayerStats (object):
    """
    Player represents a single player and all of his statistical categories.
    Every player has 'playerid', 'name' and 'home' fields.
    Additionally, depending upon which statistical categories that player
    was involved in for the game, he'll have properties such as 'passing_tds',
    'rushing_yds', 'defense_int' and 'kicking_fgm'.

    In order to know whether a paricular player belongs to a statical category,
    you may use the filtering methods of a player sequence or alternatively,
    use the has_cat method with arguments like 'passing', 'rushing', 'kicking',
    etc. (A player sequence in this case would be an instance of
    GenPlayerStats.)

    You may also inspect whether a player has a certain property by using
    the special __dict__ attribute. For example::

        if 'passing_yds' in player.__dict__:
            # Do something with player.passing_yds
    """
    def __init__(self, playerid, name, home):
        """
        Create a new Player instance with the player id (from NFL.com's
        GameCenter), the player's name (e.g., "T.Brady") and whether the
        player is playing in a home game or not.
        """
        self.playerid = playerid
        self.name = name
        self.home = home
        self._stats = OrderedDict()

    def has_cat(self, cat):
        return self.__dict__.get(cat, False)

    def __refresh_categories(self):
        for cat in nflgame.statmap.categories:
            for f in self.__dict__:
                if f.startswith(cat):
                    self.__dict__[cat] = True
                    break

    @property
    def tds(self):
        """
        Returns the total number of touchdowns credited to this player across
        all statistical categories.
        """
        n = 0
        for f, v in self.__dict__.iteritems():
            if f.endswith('tds'):
                n += v
        return n

    @property
    def stats(self):
        """
        Returns a dict of all stats for the player.
        """
        return self._stats

    def formatted_stats(self):
        """
        Returns a roughly-formatted string of all statistics for this player.
        """
        s = []
        for stat, val in self._stats.iteritems():
            s.append('%s: %s' % (stat, val))
        return ', '.join(s)

    def _add_stats(self, stats):
        for k, v in stats.iteritems():
            self.__dict__[k] = self.__dict__.get(k, 0) + v
            self._stats[k] = self.__dict__[k]
        self.__refresh_categories()

    def __str__(self):
        """
        Simply returns the player's name, e.g., "T.Brady".
        """
        return self.name

    def __add__(self, other):
        """
        Adds two players together. Only two player objects that correspond
        to the same human (i.e., GameCenter identifier) can be added together.

        If two different players are added together, an assertion will
        be raised.

        The effect of adding two player objects simply corresponds to the
        sums of all statistical values.

        Note that as soon as two players have been added, the 'home' property
        becomes undefined.
        """
        assert self.playerid == other.playerid
        assert type(self) == type(other)

        new_player = self.__class__(self.playerid, self.name, None)
        new_player._add_stats(self._stats)
        new_player._add_stats(other._stats)

        return new_player

    def __sub__(self, other):
        assert self.playerid == other.playerid
        assert type(self) == type(other)

        new_player = GamePlayerStats(self.playerid, self.name, self.home)
        new_player._add_stats(self._stats)
        for bk, bv in other._stats.iteritems():
            new_player._stats[bk] -= bv
            if new_player._stats[bk] == 0:
                del new_player._stats[bk]
            else:
                new_player.__dict__[bk] = new_player._stats[bk]

        anydiffs = False
        for k, v in new_player._stats.iteritems():
            if v > 0:
                anydiffs = True
                break
        if not anydiffs:
            return None
        return new_player

    def __getattr__(self, name):
        # If name has one of the categories as a prefix, then return
        # a default value of zero
        for cat in nflgame.statmap.categories:
            if name.startswith(cat):
                return 0
        print name
        raise AttributeError


class GamePlayerStats (PlayerStats):
    def __init__(self, playerid, name, home):
        super(GamePlayerStats, self).__init__(playerid, name, home)
        self.games = 1

    def __add__(self, other):
        new_player = super(GamePlayerStats, self).__add__(other)
        new_player.games = self.games + other.games
        return new_player


class PlayPlayerStats (PlayerStats):
    pass
